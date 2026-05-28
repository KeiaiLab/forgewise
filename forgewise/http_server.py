"""ForgeWise HTTP MCP 서버 (FastAPI 기반)."""

from __future__ import annotations

import argparse
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs

import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response
from starlette.middleware.base import BaseHTTPMiddleware

from forgewise.llm import LLMClient
from forgewise.logging import setup_logging
from forgewise.metrics import metrics_available, render_metrics
from forgewise.oauth import OAuthStore
from forgewise.protocol import handle_json_rpc

logger = logging.getLogger(__name__)



def _parse_rate_limit(spec: str) -> tuple[int, float]:
    parts = spec.strip().split("/")
    if len(parts) != 2:
        raise ValueError(f"잘못된 rate limit 형식: {spec!r}")
    max_requests = int(parts[0])
    unit = parts[1].lower()
    unit_map: dict[str, float] = {"second": 1.0, "minute": 60.0, "hour": 3600.0}
    window = unit_map.get(unit)
    if window is None:
        raise ValueError(f"지원하지 않는 시간 단위: {unit!r} (second/minute/hour)")
    return max_requests, window


class RateLimitMiddleware(BaseHTTPMiddleware):
    """IP 당 고정 윈도우 rate limiter."""

    def __init__(
        self, app: FastAPI, max_requests: int, window_seconds: float
    ) -> None:
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._buckets: dict[str, tuple[float, int]] = {}

    async def dispatch(self, request: Request, call_next: Any) -> Any:
        client_ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        start, count = self._buckets.get(client_ip, (now, 0))
        if now - start >= self.window_seconds:
            start, count = now, 0
        count += 1
        self._buckets[client_ip] = (start, count)
        if count > self.max_requests:
            return JSONResponse(
                status_code=429,
                content={"detail": "요청 한도를 초과했습니다. 잠시 후 다시 시도하세요."},
            )
        response: Any = await call_next(request)
        return response

@dataclass(frozen=True)
class HttpServerConfig:
    repo_root: Path = Path(".")
    oauth_store_path: Path = Path.home() / ".forgewise" / "oauth.sqlite3"
    require_oauth: bool = False


def create_app(config: HttpServerConfig | None = None) -> FastAPI:
    active = config or _config_from_env()
    oauth_store = OAuthStore(active.oauth_store_path)
    llm_client = LLMClient()
    app = FastAPI(title="ForgeWise GitLab MCP", version="0.2.0")

    @app.exception_handler(Exception)
    async def _global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("처리되지 않은 예외 발생: %s %s", request.method, request.url)
        return JSONResponse(
            status_code=500,
            content={"detail": "내부 서버 오류가 발생했습니다."},
        )

    cors_origins_raw = os.getenv("FORGEWISE_CORS_ORIGINS", "")
    if cors_origins_raw.strip():
        origins = [o.strip() for o in cors_origins_raw.split(",") if o.strip()]
        app.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    rate_limit_spec = os.getenv("FORGEWISE_RATE_LIMIT", "60/minute")
    rl_max, rl_window = _parse_rate_limit(rate_limit_spec)
    app.add_middleware(
        RateLimitMiddleware,  # type: ignore[arg-type]
        max_requests=rl_max,
        window_seconds=rl_window,
    )

    @app.get("/healthz")
    async def healthz() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/.well-known/oauth-authorization-server")
    async def oauth_metadata(request: Request) -> dict[str, str | list[str]]:
        base = str(request.base_url).rstrip("/")
        return {
            "issuer": base,
            "registration_endpoint": f"{base}/oauth/register",
            "authorization_endpoint": f"{base}/oauth/authorize",
            "token_endpoint": f"{base}/oauth/token",
            "code_challenge_methods_supported": ["plain", "S256"],
        }

    @app.post("/oauth/register", status_code=201)
    async def register_client(request: Request) -> dict[str, Any]:
        try:
            payload = await request.json()
            if not isinstance(payload, dict):
                raise ValueError("registration payload는 JSON object여야 합니다.")
            return oauth_store.register_client(payload)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/oauth/authorize")
    async def authorize(request: Request) -> RedirectResponse:
        params = request.query_params
        try:
            code = oauth_store.create_authorization_code(
                str(params.get("client_id") or ""),
                str(params.get("redirect_uri") or ""),
                str(params.get("scope") or ""),
                str(params.get("code_challenge") or ""),
                str(params.get("code_challenge_method") or "S256"),
            )
            location = oauth_store.redirect_with_code(
                str(params.get("redirect_uri") or ""),
                code,
                params.get("state"),
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return RedirectResponse(url=location, status_code=302)

    @app.post("/oauth/token")
    async def token(request: Request) -> dict[str, Any]:
        try:
            payload = await _read_oauth_form(request)
            grant_type = str(payload.get("grant_type") or "")
            if grant_type == "refresh_token":
                return oauth_store.exchange_refresh_token(payload)
            return oauth_store.exchange_authorization_code(payload)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.post("/api/v4/mcp")
    async def mcp_endpoint(request: Request) -> dict[str, Any]:
        if active.require_oauth and not oauth_store.validate_bearer(
            request.headers.get("Authorization")
        ):
            raise HTTPException(status_code=401, detail="유효한 Bearer token이 필요합니다.")
        payload = await request.json()
        if not isinstance(payload, dict):
            raise HTTPException(status_code=400, detail="JSON-RPC object가 필요합니다.")
        prefix = request.headers.get("X-Gitlab-Mcp-Server-Tool-Name-Prefix", "")
        return handle_json_rpc(payload, root=active.repo_root, tool_prefix=prefix, llm=llm_client)

    if metrics_available():

        @app.get("/metrics")
        async def prometheus_metrics() -> Response:
            body, content_type = render_metrics()
            return Response(content=body, media_type=content_type)

    return app


async def _read_oauth_form(request: Request) -> dict[str, Any]:
    content_type = request.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        payload = await request.json()
        if not isinstance(payload, dict):
            raise ValueError("token payload는 JSON object여야 합니다.")
        return payload
    raw = (await request.body()).decode("utf-8")
    parsed = parse_qs(raw, keep_blank_values=True)
    return {key: values[-1] for key, values in parsed.items()}


def _config_from_env() -> HttpServerConfig:
    return HttpServerConfig(
        repo_root=Path(os.getenv("FORGEWISE_REPO_ROOT", ".")).resolve(),
        oauth_store_path=Path(
            os.getenv("FORGEWISE_OAUTH_DB", str(Path.home() / ".forgewise" / "oauth.sqlite3"))
        ),
        require_oauth=os.getenv("FORGEWISE_REQUIRE_OAUTH") == "1",
    )


def main(argv: list[str] | None = None) -> int:
    setup_logging()
    parser = argparse.ArgumentParser(prog="forgewise-http")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--repo", default=os.getenv("FORGEWISE_REPO_ROOT", "."))
    parser.add_argument("--oauth-db", default=os.getenv("FORGEWISE_OAUTH_DB"))
    parser.add_argument("--require-oauth", action="store_true")
    args = parser.parse_args(argv)
    config = HttpServerConfig(
        repo_root=Path(str(args.repo)).resolve(),
        oauth_store_path=Path(str(args.oauth_db))
        if args.oauth_db
        else Path.home() / ".forgewise" / "oauth.sqlite3",
        require_oauth=bool(args.require_oauth),
    )
    logger.info("HTTP 서버 시작: host=%s port=%s", args.host, args.port)
    uvicorn.run(create_app(config), host=str(args.host), port=int(args.port), log_level="info")
    return 0


app = create_app()


if __name__ == "__main__":
    raise SystemExit(main())
