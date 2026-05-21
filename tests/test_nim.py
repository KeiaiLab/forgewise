"""Tests for forgewise NVIDIA NIM client and tool integration."""

from __future__ import annotations

from pathlib import Path
from unittest import mock

import httpx
import pytest

from forgewise.nim_client import (
    DEFAULT_MODEL,
    NIM_BASE_URL,
    NimAuthError,
    NimClient,
    NimQuotaError,
    NimUpstreamError,
)
from forgewise.tools import McpToolError, ToolRuntime, call_tool


def _mock_response(status: int, json_body: dict | None = None, headers: dict | None = None):
    return httpx.Response(
        status_code=status,
        json=json_body or {},
        headers=headers or {},
        request=httpx.Request("POST", f"{NIM_BASE_URL}/chat/completions"),
    )


def test_resolve_api_key_explicit() -> None:
    client = NimClient(api_key="nvapi-test-explicit", http_client=mock.Mock(spec=httpx.Client))
    assert client._api_key == "nvapi-test-explicit"  # noqa: SLF001 — test access


def test_resolve_api_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test-env")
    client = NimClient(http_client=mock.Mock(spec=httpx.Client))
    assert client._api_key == "nvapi-test-env"  # noqa: SLF001


def test_resolve_api_key_missing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
    monkeypatch.setattr(
        "forgewise.nim_client.SECRET_FALLBACK_PATH",
        tmp_path / "missing.txt",
    )
    with pytest.raises(NimAuthError, match="NVIDIA_API_KEY"):
        NimClient(http_client=mock.Mock(spec=httpx.Client))


def test_chat_success() -> None:
    http = mock.Mock(spec=httpx.Client)
    http.post.return_value = _mock_response(
        200,
        json_body={
            "model": "meta/llama-3.3-70b-instruct",
            "choices": [
                {
                    "message": {"content": "[critical] missing input validation"},
                    "finish_reason": "stop",
                },
            ],
        },
        headers={"x-ratelimit-remaining": "42"},
    )
    client = NimClient(api_key="nvapi-test", http_client=http)
    result = client.chat([{"role": "user", "content": "ping"}])

    assert result.text == "[critical] missing input validation"
    assert result.model == "meta/llama-3.3-70b-instruct"
    assert result.credits_remaining == 42
    assert result.finish_reason == "stop"


def test_chat_auth_error() -> None:
    http = mock.Mock(spec=httpx.Client)
    http.post.return_value = _mock_response(401)
    client = NimClient(api_key="nvapi-bad", http_client=http)
    with pytest.raises(NimAuthError):
        client.chat([{"role": "user", "content": "ping"}])


def test_chat_quota_exhausted() -> None:
    http = mock.Mock(spec=httpx.Client)
    http.post.return_value = _mock_response(429)
    client = NimClient(api_key="nvapi-test", http_client=http)
    with pytest.raises(NimQuotaError):
        client.chat([{"role": "user", "content": "ping"}])


def test_chat_upstream_5xx() -> None:
    http = mock.Mock(spec=httpx.Client)
    http.post.return_value = _mock_response(503)
    client = NimClient(api_key="nvapi-test", http_client=http)
    with pytest.raises(NimUpstreamError):
        client.chat([{"role": "user", "content": "ping"}])


def test_chat_transport_error() -> None:
    http = mock.Mock(spec=httpx.Client)
    http.post.side_effect = httpx.ConnectError("connection refused")
    client = NimClient(api_key="nvapi-test", http_client=http)
    with pytest.raises(NimUpstreamError, match="transport failure"):
        client.chat([{"role": "user", "content": "ping"}])


def test_nim_code_review_tool_success(tmp_path: Path) -> None:
    response = _mock_response(
        200,
        json_body={
            "model": DEFAULT_MODEL,
            "choices": [
                {
                    "message": {"content": "[major] consider extracting helper"},
                    "finish_reason": "stop",
                },
            ],
        },
        headers={"x-ratelimit-remaining": "100"},
    )
    runtime = ToolRuntime(root=tmp_path)
    with (
        mock.patch("forgewise.tools.NimClient") as mocked_client_cls,
        mock.patch.dict("os.environ", {"NVIDIA_API_KEY": "nvapi-test"}, clear=False),
    ):
        mocked_client = mock.Mock()
        mocked_client.chat.return_value = mock.Mock(
            text="[major] consider extracting helper",
            model=DEFAULT_MODEL,
            credits_remaining=100,
            finish_reason="stop",
        )
        mocked_client_cls.return_value = mocked_client
        _ = response  # ensure helper is referenced

        result = call_tool(
            "nim_code_review",
            {"code": "def foo(): pass", "focus": "readability"},
            runtime,
        )

    assert result["model"] == DEFAULT_MODEL
    assert result["credits_remaining"] == 100
    assert result["finish_reason"] == "stop"
    assert "advisory_review" in result
    assert "trust_boundary" in result


def test_nim_code_review_tool_quota_raises_mcp_error(tmp_path: Path) -> None:
    runtime = ToolRuntime(root=tmp_path)
    with mock.patch("forgewise.tools.NimClient") as mocked_client_cls:
        mocked_client = mock.Mock()
        mocked_client.chat.side_effect = NimQuotaError("rate limited")
        mocked_client_cls.return_value = mocked_client
        with pytest.raises(McpToolError, match="nim_quota_exhausted"):
            call_tool("nim_code_review", {"code": "x"}, runtime)


def test_nim_code_review_tool_auth_raises_mcp_error(tmp_path: Path) -> None:
    runtime = ToolRuntime(root=tmp_path)
    with mock.patch("forgewise.tools.NimClient") as mocked_client_cls:
        mocked_client = mock.Mock()
        mocked_client.chat.side_effect = NimAuthError("missing key")
        mocked_client_cls.return_value = mocked_client
        with pytest.raises(McpToolError, match="nim_auth_failure"):
            call_tool("nim_code_review", {"code": "x"}, runtime)
