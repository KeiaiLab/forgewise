from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from forgewise.http_server import HttpServerConfig, create_app


def test_http_mcp_endpoint_lists_prefixed_tools(tmp_path: Path) -> None:
    app = create_app(HttpServerConfig(repo_root=tmp_path, oauth_store_path=tmp_path / "oauth.db"))
    client = TestClient(app)

    response = client.post(
        "/api/v4/mcp",
        headers={"X-Gitlab-Mcp-Server-Tool-Name-Prefix": "gitlab_"},
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
    )

    assert response.status_code == 200
    tool_names = {tool["name"] for tool in response.json()["result"]["tools"]}
    assert "gitlab_get_mcp_server_version" in tool_names
    assert "gitlab_code_explanation_ide" in tool_names


def test_http_mcp_endpoint_calls_tool_with_default_repo(tmp_path: Path) -> None:
    app = create_app(HttpServerConfig(repo_root=tmp_path, oauth_store_path=tmp_path / "oauth.db"))
    client = TestClient(app)

    response = client.post(
        "/api/v4/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {"name": "get_mcp_server_version"},
        },
    )

    assert response.status_code == 200
    assert response.json()["result"]["structuredContent"]["protocols"] == [
        "2025-03-26",
        "2025-06-18",
    ]


def test_http_oauth_dynamic_client_registration_and_token_exchange(tmp_path: Path) -> None:
    app = create_app(HttpServerConfig(repo_root=tmp_path, oauth_store_path=tmp_path / "oauth.db"))
    client = TestClient(app)

    register = client.post(
        "/oauth/register",
        json={
            "client_name": "local-client",
            "redirect_uris": ["http://127.0.0.1:8787/callback"],
            "scope": "read_api mcp",
        },
    )
    client_info = register.json()
    authorize = client.get(
        "/oauth/authorize",
        params={
            "client_id": client_info["client_id"],
            "redirect_uri": "http://127.0.0.1:8787/callback",
            "scope": "read_api mcp",
            "code_challenge": "plain-verifier",
            "code_challenge_method": "plain",
        },
        follow_redirects=False,
    )
    code = authorize.headers["location"].split("code=", 1)[1].split("&", 1)[0]

    token = client.post(
        "/oauth/token",
        json={
            "grant_type": "authorization_code",
            "client_id": client_info["client_id"],
            "code": code,
            "redirect_uri": "http://127.0.0.1:8787/callback",
            "code_verifier": "plain-verifier",
        },
    )

    assert register.status_code == 201
    assert token.status_code == 200
    assert token.json()["token_type"] == "Bearer"
    assert token.json()["access_token"]


def test_http_mcp_rejects_invalid_bearer_token_when_auth_required(tmp_path: Path) -> None:
    app = create_app(
        HttpServerConfig(
            repo_root=tmp_path,
            oauth_store_path=tmp_path / "oauth.db",
            require_oauth=True,
        )
    )
    client = TestClient(app)

    response = client.post(
        "/api/v4/mcp",
        headers={"Authorization": "Bearer missing"},
        json={"jsonrpc": "2.0", "id": 3, "method": "tools/list"},
    )

    assert response.status_code == 401
