"""OAuth 단위 테스트 (기존 + refresh token rotation)."""

from __future__ import annotations

import base64
import hashlib
import time
from typing import Any
from unittest.mock import patch

import pytest

from forgewise.oauth import OAuthStore, _allowed_redirect_uri, _verify_pkce

# ---------------------------------------------------------------------------
# 기존 OAuth 테스트 (fixture 기반)
# ---------------------------------------------------------------------------


def test_register_client_returns_credentials(oauth_store: OAuthStore) -> None:
    result = oauth_store.register_client(
        {
            "redirect_uris": ["https://example.com/callback"],
            "scope": "read_api mcp",
            "client_name": "my-app",
        }
    )
    assert "client_id" in result
    assert "client_secret" in result
    assert result["client_name"] == "my-app"
    assert result["scope"] == "read_api mcp"
    assert result["redirect_uris"] == ["https://example.com/callback"]
    assert "registration_access_token" in result


def test_register_client_rejects_empty_redirect_uris(oauth_store: OAuthStore) -> None:
    with pytest.raises(ValueError, match="redirect_uris"):
        oauth_store.register_client({"redirect_uris": []})


def test_register_client_rejects_http_non_localhost(oauth_store: OAuthStore) -> None:
    with pytest.raises(ValueError, match="https 또는 localhost"):
        oauth_store.register_client({"redirect_uris": ["http://evil.example.com/callback"]})


def test_register_client_allows_localhost_http(oauth_store: OAuthStore) -> None:
    result = oauth_store.register_client({"redirect_uris": ["http://localhost:8080/callback"]})
    assert result["redirect_uris"] == ["http://localhost:8080/callback"]


def test_register_client_allows_127_0_0_1_http(oauth_store: OAuthStore) -> None:
    result = oauth_store.register_client({"redirect_uris": ["http://127.0.0.1:3000/cb"]})
    assert result["redirect_uris"] == ["http://127.0.0.1:3000/cb"]


def test_get_client_returns_registered_client(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    client = oauth_store.get_client(registered_client["client_id"])
    assert client.client_id == registered_client["client_id"]
    assert client.client_name == "test-client"


def test_get_client_raises_for_unknown_id(oauth_store: OAuthStore) -> None:
    with pytest.raises(ValueError, match="등록되지 않은 client_id"):
        oauth_store.get_client("nonexistent")


def test_create_authorization_code(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    code = oauth_store.create_authorization_code(
        client_id=registered_client["client_id"],
        redirect_uri="https://example.com/callback",
        scope="read_api mcp",
        code_challenge="challenge123",
        code_challenge_method="plain",
    )
    assert isinstance(code, str)
    assert len(code) > 0


def test_create_authorization_code_rejects_unregistered_redirect_uri(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    with pytest.raises(ValueError, match="등록되지 않은 redirect_uri"):
        oauth_store.create_authorization_code(
            client_id=registered_client["client_id"],
            redirect_uri="https://evil.com/steal",
            scope="read_api",
            code_challenge="challenge",
            code_challenge_method="plain",
        )


def test_create_authorization_code_requires_code_challenge(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    with pytest.raises(ValueError, match="code_challenge"):
        oauth_store.create_authorization_code(
            client_id=registered_client["client_id"],
            redirect_uri="https://example.com/callback",
            scope="read_api",
            code_challenge="",
            code_challenge_method="plain",
        )


def test_create_authorization_code_rejects_invalid_method(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    with pytest.raises(ValueError, match="plain 또는 S256"):
        oauth_store.create_authorization_code(
            client_id=registered_client["client_id"],
            redirect_uri="https://example.com/callback",
            scope="read_api",
            code_challenge="challenge",
            code_challenge_method="RS256",
        )


def test_exchange_authorization_code_plain_pkce(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    verifier = "my_verifier_string"
    code = oauth_store.create_authorization_code(
        client_id=registered_client["client_id"],
        redirect_uri="https://example.com/callback",
        scope="read_api mcp",
        code_challenge=verifier,
        code_challenge_method="plain",
    )
    token_response = oauth_store.exchange_authorization_code(
        {
            "grant_type": "authorization_code",
            "client_id": registered_client["client_id"],
            "code": code,
            "redirect_uri": "https://example.com/callback",
            "code_verifier": verifier,
        }
    )
    assert "access_token" in token_response
    assert token_response["token_type"] == "Bearer"
    assert token_response["expires_in"] == 3600


def test_exchange_authorization_code_s256_pkce(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    verifier = "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")

    code = oauth_store.create_authorization_code(
        client_id=registered_client["client_id"],
        redirect_uri="https://example.com/callback",
        scope="read_api mcp",
        code_challenge=challenge,
        code_challenge_method="S256",
    )
    token_response = oauth_store.exchange_authorization_code(
        {
            "grant_type": "authorization_code",
            "client_id": registered_client["client_id"],
            "code": code,
            "redirect_uri": "https://example.com/callback",
            "code_verifier": verifier,
        }
    )
    assert "access_token" in token_response


def test_exchange_rejects_wrong_grant_type(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    with pytest.raises(ValueError, match="authorization_code grant"):
        oauth_store.exchange_authorization_code({"grant_type": "client_credentials"})


def test_exchange_rejects_missing_fields(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    with pytest.raises(ValueError, match="client_id, code, redirect_uri, code_verifier"):
        oauth_store.exchange_authorization_code(
            {"grant_type": "authorization_code", "client_id": registered_client["client_id"]}
        )


def test_exchange_rejects_invalid_code(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    with pytest.raises(ValueError, match="찾을 수 없습니다"):
        oauth_store.exchange_authorization_code(
            {
                "grant_type": "authorization_code",
                "client_id": registered_client["client_id"],
                "code": "invalid-code",
                "redirect_uri": "https://example.com/callback",
                "code_verifier": "verifier",
            }
        )


def test_exchange_rejects_expired_code(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    code = oauth_store.create_authorization_code(
        client_id=registered_client["client_id"],
        redirect_uri="https://example.com/callback",
        scope="read_api",
        code_challenge="verifier",
        code_challenge_method="plain",
    )
    with patch("forgewise.oauth.time") as mock_time:
        mock_time.time.return_value = time.time() + 600
        with pytest.raises(ValueError, match="만료"):
            oauth_store.exchange_authorization_code(
                {
                    "grant_type": "authorization_code",
                    "client_id": registered_client["client_id"],
                    "code": code,
                    "redirect_uri": "https://example.com/callback",
                    "code_verifier": "verifier",
                }
            )


def test_exchange_rejects_wrong_redirect_uri(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    code = oauth_store.create_authorization_code(
        client_id=registered_client["client_id"],
        redirect_uri="https://example.com/callback",
        scope="read_api",
        code_challenge="verifier",
        code_challenge_method="plain",
    )
    with pytest.raises(ValueError, match="redirect_uri"):
        oauth_store.exchange_authorization_code(
            {
                "grant_type": "authorization_code",
                "client_id": registered_client["client_id"],
                "code": code,
                "redirect_uri": "https://other.com/callback",
                "code_verifier": "verifier",
            }
        )


def test_exchange_rejects_wrong_pkce_verifier(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    code = oauth_store.create_authorization_code(
        client_id=registered_client["client_id"],
        redirect_uri="https://example.com/callback",
        scope="read_api",
        code_challenge="correct_challenge",
        code_challenge_method="plain",
    )
    with pytest.raises(ValueError, match="PKCE verifier"):
        oauth_store.exchange_authorization_code(
            {
                "grant_type": "authorization_code",
                "client_id": registered_client["client_id"],
                "code": code,
                "redirect_uri": "https://example.com/callback",
                "code_verifier": "wrong_verifier",
            }
        )


def test_exchange_deletes_used_code(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    code = oauth_store.create_authorization_code(
        client_id=registered_client["client_id"],
        redirect_uri="https://example.com/callback",
        scope="read_api mcp",
        code_challenge="verifier",
        code_challenge_method="plain",
    )
    oauth_store.exchange_authorization_code(
        {
            "grant_type": "authorization_code",
            "client_id": registered_client["client_id"],
            "code": code,
            "redirect_uri": "https://example.com/callback",
            "code_verifier": "verifier",
        }
    )
    with pytest.raises(ValueError, match="찾을 수 없습니다"):
        oauth_store.exchange_authorization_code(
            {
                "grant_type": "authorization_code",
                "client_id": registered_client["client_id"],
                "code": code,
                "redirect_uri": "https://example.com/callback",
                "code_verifier": "verifier",
            }
        )


def test_validate_bearer_accepts_valid_token(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    code = oauth_store.create_authorization_code(
        client_id=registered_client["client_id"],
        redirect_uri="https://example.com/callback",
        scope="read_api mcp",
        code_challenge="verifier",
        code_challenge_method="plain",
    )
    token_resp = oauth_store.exchange_authorization_code(
        {
            "grant_type": "authorization_code",
            "client_id": registered_client["client_id"],
            "code": code,
            "redirect_uri": "https://example.com/callback",
            "code_verifier": "verifier",
        }
    )
    assert oauth_store.validate_bearer(f"Bearer {token_resp['access_token']}", "mcp")


def test_validate_bearer_rejects_invalid_token(oauth_store: OAuthStore) -> None:
    assert not oauth_store.validate_bearer("Bearer invalid-token")


def test_validate_bearer_rejects_missing_header(oauth_store: OAuthStore) -> None:
    assert not oauth_store.validate_bearer(None)
    assert not oauth_store.validate_bearer("")
    assert not oauth_store.validate_bearer("Basic abc123")


def test_validate_bearer_rejects_expired_token(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    code = oauth_store.create_authorization_code(
        client_id=registered_client["client_id"],
        redirect_uri="https://example.com/callback",
        scope="read_api mcp",
        code_challenge="verifier",
        code_challenge_method="plain",
    )
    token_resp = oauth_store.exchange_authorization_code(
        {
            "grant_type": "authorization_code",
            "client_id": registered_client["client_id"],
            "code": code,
            "redirect_uri": "https://example.com/callback",
            "code_verifier": "verifier",
        }
    )
    with patch("forgewise.oauth.time") as mock_time:
        mock_time.time.return_value = time.time() + 7200
        assert not oauth_store.validate_bearer(f"Bearer {token_resp['access_token']}")


def test_validate_bearer_checks_required_scope(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    code = oauth_store.create_authorization_code(
        client_id=registered_client["client_id"],
        redirect_uri="https://example.com/callback",
        scope="read_api mcp",
        code_challenge="verifier",
        code_challenge_method="plain",
    )
    token_resp = oauth_store.exchange_authorization_code(
        {
            "grant_type": "authorization_code",
            "client_id": registered_client["client_id"],
            "code": code,
            "redirect_uri": "https://example.com/callback",
            "code_verifier": "verifier",
        }
    )
    assert oauth_store.validate_bearer(f"Bearer {token_resp['access_token']}", "mcp")
    assert not oauth_store.validate_bearer(f"Bearer {token_resp['access_token']}", "admin")


def test_redirect_with_code_appends_params(oauth_store: OAuthStore) -> None:
    url = oauth_store.redirect_with_code("https://example.com/callback", "abc", "state123")
    assert "code=abc" in url
    assert "state=state123" in url


def test_redirect_with_code_without_state(oauth_store: OAuthStore) -> None:
    url = oauth_store.redirect_with_code("https://example.com/callback", "abc")
    assert "code=abc" in url
    assert "state" not in url


def test_verify_pkce_plain() -> None:
    _verify_pkce("verifier", "verifier", "plain")


def test_verify_pkce_s256() -> None:
    verifier = "test_verifier_value"
    digest = hashlib.sha256(verifier.encode("ascii")).digest()
    challenge = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    _verify_pkce(verifier, challenge, "S256")


def test_verify_pkce_rejects_mismatch() -> None:
    with pytest.raises(ValueError, match="PKCE verifier"):
        _verify_pkce("wrong", "expected", "plain")


def test_allowed_redirect_uri() -> None:
    assert _allowed_redirect_uri("https://example.com/cb")
    assert _allowed_redirect_uri("http://localhost:3000/cb")
    assert _allowed_redirect_uri("http://127.0.0.1:8080/cb")
    assert not _allowed_redirect_uri("http://evil.example.com/cb")
    assert not _allowed_redirect_uri("ftp://example.com/cb")


# ---------------------------------------------------------------------------
# Refresh token rotation 테스트 (fixture 기반)
# ---------------------------------------------------------------------------


def _issue_tokens(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> dict[str, str | int]:
    """authorization code 발급 -> access + refresh token 교환까지 수행."""
    code = oauth_store.create_authorization_code(
        client_id=registered_client["client_id"],
        redirect_uri="https://example.com/callback",
        scope="read_api mcp",
        code_challenge="plain-verifier",
        code_challenge_method="plain",
    )
    return oauth_store.exchange_authorization_code(
        {
            "grant_type": "authorization_code",
            "client_id": registered_client["client_id"],
            "code": code,
            "redirect_uri": "https://example.com/callback",
            "code_verifier": "plain-verifier",
        }
    )


# -- exchange_authorization_code 에서 refresh_token 발급 확인 --


def test_exchange_returns_refresh_token(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    """authorization code 교환 시 refresh_token이 응답에 포함되어야 한다."""
    result = _issue_tokens(oauth_store, registered_client)

    assert "refresh_token" in result
    assert result["refresh_token"]
    assert result["token_type"] == "Bearer"
    assert result["expires_in"] == 3600


# -- exchange_refresh_token 정상 동작 --


def test_refresh_token_exchange_returns_new_pair(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    """refresh_token 교환 시 새 access_token + refresh_token 쌍이 발급되어야 한다."""
    first = _issue_tokens(oauth_store, registered_client)

    second = oauth_store.exchange_refresh_token(
        {
            "grant_type": "refresh_token",
            "refresh_token": first["refresh_token"],
        }
    )

    assert second["access_token"] != first["access_token"]
    assert second["refresh_token"] != first["refresh_token"]
    assert second["token_type"] == "Bearer"
    assert second["expires_in"] == 3600
    assert second["scope"] == first["scope"]


# -- rotation: 기존 토큰 무효화 --


def test_old_access_token_invalid_after_refresh(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    """refresh 후 기존 access_token은 무효여야 한다."""
    first = _issue_tokens(oauth_store, registered_client)

    # 기존 access_token 유효 확인
    assert oauth_store.validate_bearer(f"Bearer {first['access_token']}")

    oauth_store.exchange_refresh_token(
        {
            "grant_type": "refresh_token",
            "refresh_token": first["refresh_token"],
        }
    )

    # refresh 후 기존 access_token 무효
    assert not oauth_store.validate_bearer(f"Bearer {first['access_token']}")


def test_old_refresh_token_invalid_after_refresh(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    """refresh 후 기존 refresh_token으로 재사용 불가해야 한다 (replay 방지)."""
    first = _issue_tokens(oauth_store, registered_client)

    oauth_store.exchange_refresh_token(
        {
            "grant_type": "refresh_token",
            "refresh_token": first["refresh_token"],
        }
    )

    with pytest.raises(ValueError, match="유효하지 않은 refresh_token"):
        oauth_store.exchange_refresh_token(
            {
                "grant_type": "refresh_token",
                "refresh_token": first["refresh_token"],
            }
        )


# -- 새 토큰 쌍으로 인증 가능 --


def test_new_access_token_valid_after_refresh(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    """refresh로 발급된 새 access_token은 유효해야 한다."""
    first = _issue_tokens(oauth_store, registered_client)

    second = oauth_store.exchange_refresh_token(
        {
            "grant_type": "refresh_token",
            "refresh_token": first["refresh_token"],
        }
    )

    assert oauth_store.validate_bearer(f"Bearer {second['access_token']}")


def test_chained_refresh(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    """연쇄 refresh: 2번째 refresh_token으로도 교환 가능해야 한다."""
    first = _issue_tokens(oauth_store, registered_client)

    second = oauth_store.exchange_refresh_token(
        {
            "grant_type": "refresh_token",
            "refresh_token": first["refresh_token"],
        }
    )
    third = oauth_store.exchange_refresh_token(
        {
            "grant_type": "refresh_token",
            "refresh_token": second["refresh_token"],
        }
    )

    assert third["access_token"] != second["access_token"]
    assert third["refresh_token"] != second["refresh_token"]
    assert oauth_store.validate_bearer(f"Bearer {third['access_token']}")


# -- 만료 검증 --


def test_expired_refresh_token_rejected(
    oauth_store: OAuthStore, registered_client: dict[str, Any]
) -> None:
    """만료된 refresh_token은 거부되어야 한다."""
    first = _issue_tokens(oauth_store, registered_client)

    # 8일 후로 시간 이동 (refresh token 7일 만료 초과)
    future = time.time() + 8 * 24 * 3600
    with patch("forgewise.oauth.time") as mock_time:
        mock_time.time.return_value = future
        with pytest.raises(ValueError, match="refresh_token이 만료되었습니다"):
            oauth_store.exchange_refresh_token(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": first["refresh_token"],
                }
            )


# -- 에러 케이스 --


def test_refresh_requires_grant_type(oauth_store: OAuthStore) -> None:
    """grant_type이 refresh_token이 아니면 에러."""
    with pytest.raises(ValueError, match="refresh_token grant만 지원합니다"):
        oauth_store.exchange_refresh_token(
            {
                "grant_type": "authorization_code",
                "refresh_token": "some-token",
            }
        )


def test_refresh_requires_refresh_token_field(oauth_store: OAuthStore) -> None:
    """refresh_token 필드가 비어 있으면 에러."""
    with pytest.raises(ValueError, match="refresh_token이 필요합니다"):
        oauth_store.exchange_refresh_token(
            {
                "grant_type": "refresh_token",
                "refresh_token": "",
            }
        )


def test_refresh_with_unknown_token(oauth_store: OAuthStore) -> None:
    """존재하지 않는 refresh_token이면 에러."""
    with pytest.raises(ValueError, match="유효하지 않은 refresh_token"):
        oauth_store.exchange_refresh_token(
            {
                "grant_type": "refresh_token",
                "refresh_token": "nonexistent-token",
            }
        )
