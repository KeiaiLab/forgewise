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


# ---------------------------------------------------------------------------
# OAuth 토큰 해싱 테스트 (#28)
# ---------------------------------------------------------------------------


def test_oauth_token_stored_as_sha256_hash(tmp_path: Path) -> None:
    """access_token 은 DB 에 SHA-256 해시로 저장되고, 평문은 응답에만 반환."""
    import hashlib
    import sqlite3

    app = create_app(HttpServerConfig(repo_root=tmp_path, oauth_store_path=tmp_path / "oauth.db"))
    client = TestClient(app)

    # DCR → authorize → token exchange
    reg = client.post(
        "/oauth/register",
        json={
            "client_name": "hash-test",
            "redirect_uris": ["http://127.0.0.1:9999/cb"],
            "scope": "read_api mcp",
        },
    ).json()
    auth = client.get(
        "/oauth/authorize",
        params={
            "client_id": reg["client_id"],
            "redirect_uri": "http://127.0.0.1:9999/cb",
            "scope": "read_api mcp",
            "code_challenge": "plain-v",
            "code_challenge_method": "plain",
        },
        follow_redirects=False,
    )
    code = auth.headers["location"].split("code=", 1)[1].split("&", 1)[0]
    tok = client.post(
        "/oauth/token",
        json={
            "grant_type": "authorization_code",
            "client_id": reg["client_id"],
            "code": code,
            "redirect_uri": "http://127.0.0.1:9999/cb",
            "code_verifier": "plain-v",
        },
    ).json()

    plaintext = tok["access_token"]
    expected_hash = hashlib.sha256(plaintext.encode("utf-8")).hexdigest()

    # DB 에 평문이 아닌 해시가 저장되어 있는지 확인
    conn = sqlite3.connect(tmp_path / "oauth.db")
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT access_token FROM tokens").fetchone()
    conn.close()

    assert row is not None
    assert str(row["access_token"]) == expected_hash
    assert str(row["access_token"]) != plaintext


def test_oauth_client_secret_stored_as_hash(tmp_path: Path) -> None:
    """client_secret 은 DB 에 SHA-256 해시로 저장된다."""
    import hashlib
    import sqlite3

    app = create_app(HttpServerConfig(repo_root=tmp_path, oauth_store_path=tmp_path / "oauth.db"))
    client = TestClient(app)

    reg = client.post(
        "/oauth/register",
        json={
            "client_name": "secret-hash-test",
            "redirect_uris": ["http://127.0.0.1:9999/cb"],
            "scope": "read_api mcp",
        },
    ).json()

    plaintext_secret = reg["client_secret"]
    expected_hash = hashlib.sha256(plaintext_secret.encode("utf-8")).hexdigest()

    conn = sqlite3.connect(tmp_path / "oauth.db")
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        "SELECT client_secret FROM clients WHERE client_id = ?",
        (reg["client_id"],),
    ).fetchone()
    conn.close()

    assert row is not None
    assert str(row["client_secret"]) == expected_hash
    assert str(row["client_secret"]) != plaintext_secret


def test_oauth_hashed_token_validates_correctly(tmp_path: Path) -> None:
    """해시 저장된 토큰으로 Bearer 인증이 정상 동작한다."""
    app = create_app(
        HttpServerConfig(
            repo_root=tmp_path,
            oauth_store_path=tmp_path / "oauth.db",
            require_oauth=True,
        )
    )
    client = TestClient(app)

    # 전체 OAuth 플로우 수행
    reg = client.post(
        "/oauth/register",
        json={
            "client_name": "auth-test",
            "redirect_uris": ["http://127.0.0.1:9999/cb"],
            "scope": "read_api mcp",
        },
    ).json()
    auth = client.get(
        "/oauth/authorize",
        params={
            "client_id": reg["client_id"],
            "redirect_uri": "http://127.0.0.1:9999/cb",
            "scope": "read_api mcp",
            "code_challenge": "test-verifier",
            "code_challenge_method": "plain",
        },
        follow_redirects=False,
    )
    code = auth.headers["location"].split("code=", 1)[1].split("&", 1)[0]
    tok = client.post(
        "/oauth/token",
        json={
            "grant_type": "authorization_code",
            "client_id": reg["client_id"],
            "code": code,
            "redirect_uri": "http://127.0.0.1:9999/cb",
            "code_verifier": "test-verifier",
        },
    ).json()

    # 평문 토큰으로 API 호출 → 서버 내부에서 해시 비교로 검증
    resp = client.post(
        "/api/v4/mcp",
        headers={"Authorization": f"Bearer {tok['access_token']}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
    )
    assert resp.status_code == 200


def test_oauth_verify_client_secret(tmp_path: Path) -> None:
    """verify_client_secret 메서드가 평문 → 해시 비교로 동작한다."""
    from forgewise.oauth import OAuthStore

    store = OAuthStore(tmp_path / "oauth.db")
    reg = store.register_client(
        {
            "client_name": "verify-test",
            "redirect_uris": ["http://127.0.0.1:9999/cb"],
            "scope": "read_api mcp",
        }
    )

    # 올바른 secret → True
    assert store.verify_client_secret(reg["client_id"], reg["client_secret"]) is True
    # 잘못된 secret → False
    assert store.verify_client_secret(reg["client_id"], "wrong-secret") is False
    # 존재하지 않는 client → False
    assert store.verify_client_secret("nonexistent", reg["client_secret"]) is False
