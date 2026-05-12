from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from forgewise.gitlab_client import GitLabClient, GitLabConfig
from forgewise.protocol import handle_json_rpc


def _transport(
    requests: list[httpx.Request],
    payload: object | None = None,
    status_code: int = 200,
) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return httpx.Response(status_code, json={} if payload is None else payload)

    return httpx.MockTransport(handler)


def test_gitlab_client_get_issue_uses_gitlab_rest_contract() -> None:
    requests: list[httpx.Request] = []
    transport = _transport(requests, {"iid": 42, "title": "bug"})
    with httpx.Client(transport=transport) as http:
        client = GitLabClient(
            GitLabConfig(base_url="https://gitlab.example.com", token="token"),
            http_client=http,
        )

        result = client.get_issue("group/project", 42)

    assert result["data"]["title"] == "bug"
    assert requests[0].method == "GET"
    assert (
        str(requests[0].url)
        == "https://gitlab.example.com/api/v4/projects/group%2Fproject/issues/42"
    )
    assert requests[0].headers["authorization"] == "Bearer token"


def test_gitlab_client_redacts_token_from_http_errors() -> None:
    requests: list[httpx.Request] = []
    transport = _transport(requests, {"message": "bad"}, status_code=500)
    with httpx.Client(transport=transport) as http:
        client = GitLabClient(
            GitLabConfig(base_url="https://gitlab.example.com", token="super-secret-token"),
            http_client=http,
        )

        with pytest.raises(RuntimeError) as exc:
            client.get_issue("project", 1)

    assert "super-secret-token" not in str(exc.value)
    assert "500" in str(exc.value)


def test_gitlab_mutation_tools_fail_closed(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GITLAB_TOKEN", "token")
    monkeypatch.delenv("FORGEWISE_ENABLE_MUTATIONS", raising=False)

    response = handle_json_rpc(
        {
            "jsonrpc": "2.0",
            "id": 10,
            "method": "tools/call",
            "params": {
                "name": "create_issue",
                "arguments": {"repo": str(tmp_path), "id": "project", "title": "blocked"},
            },
        }
    )

    assert response["error"]["code"] == -32602
    assert "FORGEWISE_ENABLE_MUTATIONS" in response["error"]["message"]


def test_gitlab_tools_can_use_injected_http_transport(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    requests: list[httpx.Request] = []
    transport = _transport(requests, {"iid": 42})
    monkeypatch.setenv("GITLAB_TOKEN", "token")
    monkeypatch.setenv("GITLAB_BASE_URL", "https://gitlab.example.com")

    with httpx.Client(transport=transport) as http:
        response = handle_json_rpc(
            {
                "jsonrpc": "2.0",
                "id": 11,
                "method": "tools/call",
                "params": {
                    "name": "get_issue",
                    "arguments": {"repo": str(tmp_path), "id": "group/project", "issue_iid": 42},
                },
            },
            gitlab_http_client=http,
        )

    result = response["result"]["structuredContent"]
    assert json.loads(response["result"]["content"][0]["text"])["data"]["iid"] == 42
    assert result["feature"] == "get_issue"
    assert requests[0].method == "GET"
