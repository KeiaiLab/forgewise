from __future__ import annotations

import base64
import hashlib
import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

from authlib.common.security import generate_token  # type: ignore[import-untyped]


@dataclass(frozen=True)
class RegisteredClient:
    client_id: str
    client_secret: str
    redirect_uris: list[str]
    scope: str
    client_name: str


class OAuthStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def register_client(self, metadata: dict[str, Any]) -> dict[str, Any]:
        redirect_uris = _string_list(metadata.get("redirect_uris"))
        if not redirect_uris:
            raise ValueError("redirect_uris가 필요합니다.")
        for uri in redirect_uris:
            if not _allowed_redirect_uri(uri):
                raise ValueError("redirect_uri는 https 또는 localhost/127.0.0.1 http만 허용합니다.")
        client = RegisteredClient(
            client_id=_generate_token(32),
            client_secret=_generate_token(48),
            redirect_uris=redirect_uris,
            scope=str(metadata.get("scope") or "read_api mcp"),
            client_name=str(metadata.get("client_name") or "forgewise-client"),
        )
        registration_token = _generate_token(48)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO clients (
                    client_id, client_secret, redirect_uris, scope, client_name,
                    registration_access_token, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    client.client_id,
                    client.client_secret,
                    json.dumps(client.redirect_uris, ensure_ascii=False),
                    client.scope,
                    client.client_name,
                    registration_token,
                    int(time.time()),
                ),
            )
        return {
            "client_id": client.client_id,
            "client_secret": client.client_secret,
            "client_name": client.client_name,
            "redirect_uris": client.redirect_uris,
            "scope": client.scope,
            "token_endpoint_auth_method": "client_secret_post",
            "registration_access_token": registration_token,
        }

    def create_authorization_code(
        self,
        client_id: str,
        redirect_uri: str,
        scope: str,
        code_challenge: str,
        code_challenge_method: str,
    ) -> str:
        client = self.get_client(client_id)
        if redirect_uri not in client.redirect_uris:
            raise ValueError("등록되지 않은 redirect_uri입니다.")
        if not code_challenge:
            raise ValueError("PKCE code_challenge가 필요합니다.")
        if code_challenge_method not in {"plain", "S256"}:
            raise ValueError("PKCE method는 plain 또는 S256만 지원합니다.")
        code = _generate_token(32)
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO authorization_codes (
                    code, client_id, redirect_uri, scope, code_challenge,
                    code_challenge_method, expires_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    code,
                    client_id,
                    redirect_uri,
                    scope or client.scope,
                    code_challenge,
                    code_challenge_method,
                    int(time.time()) + 300,
                ),
            )
        return code

    def redirect_with_code(self, redirect_uri: str, code: str, state: str | None = None) -> str:
        params = {"code": code}
        if state:
            params["state"] = state
        separator = "&" if "?" in redirect_uri else "?"
        return f"{redirect_uri}{separator}{urlencode(params)}"

    def exchange_authorization_code(self, form: dict[str, Any]) -> dict[str, Any]:
        if form.get("grant_type") != "authorization_code":
            raise ValueError("authorization_code grant만 지원합니다.")
        client_id = str(form.get("client_id") or "")
        code = str(form.get("code") or "")
        redirect_uri = str(form.get("redirect_uri") or "")
        code_verifier = str(form.get("code_verifier") or "")
        if not all((client_id, code, redirect_uri, code_verifier)):
            raise ValueError("client_id, code, redirect_uri, code_verifier가 필요합니다.")
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT code, client_id, redirect_uri, scope, code_challenge,
                       code_challenge_method, expires_at
                FROM authorization_codes
                WHERE code = ? AND client_id = ?
                """,
                (code, client_id),
            ).fetchone()
            if row is None:
                raise ValueError("authorization code를 찾을 수 없습니다.")
            if int(row["expires_at"]) < int(time.time()):
                raise ValueError("authorization code가 만료되었습니다.")
            if str(row["redirect_uri"]) != redirect_uri:
                raise ValueError("redirect_uri가 authorization 요청과 다릅니다.")
            _verify_pkce(
                code_verifier, str(row["code_challenge"]), str(row["code_challenge_method"])
            )
            access_token = _generate_token(48)
            expires_at = int(time.time()) + 3600
            conn.execute("DELETE FROM authorization_codes WHERE code = ?", (code,))
            conn.execute(
                """
                INSERT INTO tokens (access_token, client_id, scope, expires_at)
                VALUES (?, ?, ?, ?)
                """,
                (access_token, client_id, str(row["scope"]), expires_at),
            )
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": str(row["scope"]),
        }

    def validate_bearer(self, authorization: str | None, required_scope: str = "mcp") -> bool:
        if not authorization or not authorization.startswith("Bearer "):
            return False
        token = authorization.removeprefix("Bearer ").strip()
        with self._connect() as conn:
            row = conn.execute(
                "SELECT scope, expires_at FROM tokens WHERE access_token = ?",
                (token,),
            ).fetchone()
        if row is None or int(row["expires_at"]) < int(time.time()):
            return False
        scopes = set(str(row["scope"]).split())
        return required_scope in scopes

    def get_client(self, client_id: str) -> RegisteredClient:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT client_id, client_secret, redirect_uris, scope, client_name
                FROM clients
                WHERE client_id = ?
                """,
                (client_id,),
            ).fetchone()
        if row is None:
            raise ValueError("등록되지 않은 client_id입니다.")
        return RegisteredClient(
            client_id=str(row["client_id"]),
            client_secret=str(row["client_secret"]),
            redirect_uris=list(json.loads(str(row["redirect_uris"]))),
            scope=str(row["scope"]),
            client_name=str(row["client_name"]),
        )

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS clients (
                    client_id TEXT PRIMARY KEY,
                    client_secret TEXT NOT NULL,
                    redirect_uris TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    registration_access_token TEXT NOT NULL,
                    created_at INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS authorization_codes (
                    code TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    redirect_uri TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    code_challenge TEXT NOT NULL,
                    code_challenge_method TEXT NOT NULL,
                    expires_at INTEGER NOT NULL
                );
                CREATE TABLE IF NOT EXISTS tokens (
                    access_token TEXT PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    scope TEXT NOT NULL,
                    expires_at INTEGER NOT NULL
                );
                """
            )


def _verify_pkce(verifier: str, challenge: str, method: str) -> None:
    if method == "plain":
        computed = verifier
    else:
        digest = hashlib.sha256(verifier.encode("ascii")).digest()
        computed = base64.urlsafe_b64encode(digest).decode("ascii").rstrip("=")
    if computed != challenge:
        raise ValueError("PKCE verifier가 code_challenge와 일치하지 않습니다.")


def _generate_token(length: int) -> str:
    return str(generate_token(length))


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str)]


def _allowed_redirect_uri(uri: str) -> bool:
    return (
        uri.startswith("https://")
        or uri.startswith("http://127.0.0.1")
        or uri.startswith("http://localhost")
    )
