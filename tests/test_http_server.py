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

    # DCR -> authorize -> token exchange
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

    # 평문 토큰으로 API 호출 -> 서버 내부에서 해시 비교로 검증
    resp = client.post(
        "/api/v4/mcp",
        headers={"Authorization": f"Bearer {tok['access_token']}"},
        json={"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
    )
    assert resp.status_code == 200


def test_oauth_verify_client_secret(tmp_path: Path) -> None:
    """verify_client_secret 메서드가 평문 -> 해시 비교로 동작한다."""
    from forgewise.oauth import OAuthStore

    store = OAuthStore(tmp_path / "oauth.db")
    reg = store.register_client(
        {
            "client_name": "verify-test",
            "redirect_uris": ["http://127.0.0.1:9999/cb"],
            "scope": "read_api mcp",
        }
    )

    # 올바른 secret -> True
    assert store.verify_client_secret(reg["client_id"], reg["client_secret"]) is True
    # 잘못된 secret -> False
    assert store.verify_client_secret(reg["client_id"], "wrong-secret") is False
    # 존재하지 않는 client -> False
    assert store.verify_client_secret("nonexistent", reg["client_secret"]) is False


# ---------------------------------------------------------------------------
# OAuth refresh token HTTP 테스트
# ---------------------------------------------------------------------------


def _do_full_oauth_flow(http_client: TestClient) -> dict[str, str]:
    """클라이언트 등록 -> 인가 -> 토큰 교환까지 수행하고 token 응답을 반환."""
    register = http_client.post(
        "/oauth/register",
        json={
            "client_name": "refresh-test",
            "redirect_uris": ["http://127.0.0.1:8787/callback"],
            "scope": "read_api mcp",
        },
    )
    client_info = register.json()
    authorize = http_client.get(
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

    token_resp = http_client.post(
        "/oauth/token",
        json={
            "grant_type": "authorization_code",
            "client_id": client_info["client_id"],
            "code": code,
            "redirect_uri": "http://127.0.0.1:8787/callback",
            "code_verifier": "plain-verifier",
        },
    )
    return token_resp.json()


def test_http_token_exchange_returns_refresh_token(tmp_path: Path) -> None:
    """HTTP /oauth/token 응답에 refresh_token이 포함되어야 한다."""
    app = create_app(HttpServerConfig(repo_root=tmp_path, oauth_store_path=tmp_path / "oauth.db"))
    http_client = TestClient(app)
    token_data = _do_full_oauth_flow(http_client)

    assert "refresh_token" in token_data
    assert token_data["refresh_token"]
    assert token_data["token_type"] == "Bearer"


def test_http_refresh_token_exchange(tmp_path: Path) -> None:
    """HTTP /oauth/token grant_type=refresh_token 으로 새 토큰 쌍 발급."""
    app = create_app(HttpServerConfig(repo_root=tmp_path, oauth_store_path=tmp_path / "oauth.db"))
    http_client = TestClient(app)
    first = _do_full_oauth_flow(http_client)

    refresh_resp = http_client.post(
        "/oauth/token",
        json={
            "grant_type": "refresh_token",
            "refresh_token": first["refresh_token"],
        },
    )

    assert refresh_resp.status_code == 200
    second = refresh_resp.json()
    assert second["access_token"] != first["access_token"]
    assert second["refresh_token"] != first["refresh_token"]
    assert second["token_type"] == "Bearer"


def test_http_refresh_with_invalid_token_returns_400(tmp_path: Path) -> None:
    """존재하지 않는 refresh_token 으로 요청 시 400 반환."""
    app = create_app(HttpServerConfig(repo_root=tmp_path, oauth_store_path=tmp_path / "oauth.db"))
    http_client = TestClient(app)

    resp = http_client.post(
        "/oauth/token",
        json={
            "grant_type": "refresh_token",
            "refresh_token": "invalid-token",
        },
    )

    assert resp.status_code == 400


def test_http_refresh_rotation_invalidates_old_token(tmp_path: Path) -> None:
    """refresh 후 기존 refresh_token 재사용 시 400 반환 (rotation 검증)."""
    app = create_app(HttpServerConfig(repo_root=tmp_path, oauth_store_path=tmp_path / "oauth.db"))
    http_client = TestClient(app)
    first = _do_full_oauth_flow(http_client)

    # 첫 번째 refresh 성공
    http_client.post(
        "/oauth/token",
        json={
            "grant_type": "refresh_token",
            "refresh_token": first["refresh_token"],
        },
    )

    # 기존 refresh_token 재사용 시도 -> 400
    replay = http_client.post(
        "/oauth/token",
        json={
            "grant_type": "refresh_token",
            "refresh_token": first["refresh_token"],
        },
    )
    assert replay.status_code == 400


def test_http_refresh_via_form_urlencoded(tmp_path: Path) -> None:
    """application/x-www-form-urlencoded 로도 refresh_token 교환 가능."""
    app = create_app(HttpServerConfig(repo_root=tmp_path, oauth_store_path=tmp_path / "oauth.db"))
    http_client = TestClient(app)
    first = _do_full_oauth_flow(http_client)

    resp = http_client.post(
        "/oauth/token",
        data=f"grant_type=refresh_token&refresh_token={first['refresh_token']}",
        headers={"content-type": "application/x-www-form-urlencoded"},
    )

    assert resp.status_code == 200
    assert resp.json()["access_token"]
    assert resp.json()["refresh_token"]
