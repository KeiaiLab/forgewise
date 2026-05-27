from __future__ import annotations

import base64
import hashlib
import time
from typing import Any
from unittest.mock import patch

import pytest

from forgewise.oauth import OAuthStore, _allowed_redirect_uri, _verify_pkce


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
