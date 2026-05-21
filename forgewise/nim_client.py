"""NVIDIA NIM API client — OpenAI-compatible chat completions.

Endpoint: ``https://integrate.api.nvidia.com/v1/chat/completions``

API key (`nvapi-...`) sources (priority order):

1. Explicit ``api_key`` constructor argument
2. ``NVIDIA_API_KEY`` environment variable
3. File at ``~/.secrets/nvidia/nim-api-key.txt`` (mode 0600)

Quota: NVIDIA Developer Program free tier — 1000 credits/month default,
up to 5000 on request, 40 req/min rate limit.

Trust boundary: LLM output is advisory only — caller must treat as
hint, not authoritative.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import httpx

NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
DEFAULT_MODEL = "meta/llama-3.3-70b-instruct"
DEFAULT_TIMEOUT_SECONDS = 30.0
SECRET_FALLBACK_PATH = Path.home() / ".secrets" / "nvidia" / "nim-api-key.txt"


class NimQuotaError(RuntimeError):
    """Quota exhausted / rate-limited (HTTP 429) — caller should retry later."""


class NimAuthError(RuntimeError):
    """Auth failure (HTTP 401/403) — API key missing or invalid."""


class NimUpstreamError(RuntimeError):
    """5xx or transport error from NIM endpoint."""


@dataclass(frozen=True)
class NimResponse:
    """Single chat completion result with quota metadata."""

    text: str
    model: str
    credits_remaining: int | None
    finish_reason: str | None


def _resolve_api_key(explicit: str | None) -> str:
    if explicit:
        return explicit
    env_value = os.environ.get("NVIDIA_API_KEY", "").strip()
    if env_value:
        return env_value
    if SECRET_FALLBACK_PATH.exists():
        return SECRET_FALLBACK_PATH.read_text(encoding="utf-8").strip()
    raise NimAuthError(
        "NVIDIA NIM API key not found. Set NVIDIA_API_KEY or create "
        f"{SECRET_FALLBACK_PATH} (mode 0600) with a nvapi-... token.",
    )


class NimClient:
    """Thin OpenAI-compatible wrapper for NVIDIA NIM hosted endpoints."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str = DEFAULT_MODEL,
        base_url: str = NIM_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        http_client: httpx.Client | None = None,
    ) -> None:
        self._api_key = _resolve_api_key(api_key)
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._http = http_client

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        max_tokens: int = 1024,
        temperature: float = 0.2,
    ) -> NimResponse:
        payload = {
            "model": self._model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        url = f"{self._base_url}/chat/completions"
        client = self._http or httpx.Client(timeout=self._timeout)
        try:
            response = client.post(url, headers=headers, json=payload)
        except httpx.HTTPError as exc:
            raise NimUpstreamError(f"NIM transport failure: {exc}") from exc
        finally:
            if self._http is None:
                client.close()

        if response.status_code in (401, 403):
            raise NimAuthError(f"NIM auth failed (HTTP {response.status_code})")
        if response.status_code == 429:
            raise NimQuotaError(
                "NIM rate limit / quota exhausted (HTTP 429) — retry after cooldown",
            )
        if response.status_code >= 500:
            raise NimUpstreamError(f"NIM upstream error (HTTP {response.status_code})")
        if response.status_code != 200:
            raise NimUpstreamError(
                f"NIM unexpected status (HTTP {response.status_code}): {response.text[:200]}",
            )

        body = response.json()
        try:
            choice = body["choices"][0]
            text = choice["message"]["content"]
            finish_reason = choice.get("finish_reason")
        except (KeyError, IndexError, TypeError) as exc:
            raise NimUpstreamError(f"NIM response shape unexpected: {exc}") from exc

        remaining_header = response.headers.get("x-ratelimit-remaining")
        credits_remaining = int(remaining_header) if remaining_header is not None else None

        return NimResponse(
            text=text,
            model=body.get("model", self._model),
            credits_remaining=credits_remaining,
            finish_reason=finish_reason,
        )
