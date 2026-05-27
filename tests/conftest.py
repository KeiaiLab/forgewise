from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx
import pytest

from forgewise.oauth import OAuthStore


@pytest.fixture()
def sample_repo(tmp_path: Path) -> Path:
    source = tmp_path / "service.py"
    source.write_text(
        "\n".join(
            [
                "import subprocess",
                "",
                "API_TOKEN = 'abc123'",
                "",
                "class BillingService:",
                "    def total(self, prices: list[int]) -> int:",
                "        return sum(prices)",
                "",
                "def run(command: str) -> str:",
                "    return subprocess.check_output(command, shell=True, text=True)",
                "",
                "def unsafe(expr: str) -> object:",
                "    return eval(expr)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return tmp_path


@pytest.fixture()
def minimal_repo(tmp_path: Path) -> Path:
    (tmp_path / "app.py").write_text(
        "def add(a: int, b: int) -> int:\n    return a + b\n",
        encoding="utf-8",
    )
    return tmp_path


def make_gitlab_transport(
    payload: object | None = None,
    status_code: int = 200,
) -> tuple[list[httpx.Request], httpx.MockTransport]:
    requests: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status_code, json={} if payload is None else payload)

    return requests, httpx.MockTransport(handler)


@pytest.fixture()
def gitlab_transport() -> tuple[list[httpx.Request], httpx.MockTransport]:
    return make_gitlab_transport()


@pytest.fixture()
def gitlab_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITLAB_TOKEN", "test-token")
    monkeypatch.setenv("GITLAB_BASE_URL", "https://gitlab.example.com")


@pytest.fixture()
def oauth_store(tmp_path: Path) -> OAuthStore:
    return OAuthStore(tmp_path / "oauth.sqlite3")


@pytest.fixture()
def registered_client(oauth_store: OAuthStore) -> dict[str, Any]:
    return oauth_store.register_client(
        {
            "redirect_uris": ["https://example.com/callback"],
            "scope": "read_api mcp",
            "client_name": "test-client",
        }
    )
