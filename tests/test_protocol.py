from __future__ import annotations

from pathlib import Path

from forgewise.protocol import DEFAULT_PROTOCOL, SUPPORTED_PROTOCOLS, handle_json_rpc


def test_initialize_returns_supported_protocol() -> None:
    response = handle_json_rpc(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "2025-03-26"},
        }
    )
    assert response["id"] == 1
    assert response["result"]["protocolVersion"] == "2025-03-26"
    assert response["result"]["serverInfo"]["name"] == "forgewise"


def test_initialize_falls_back_to_default_for_unsupported_protocol() -> None:
    response = handle_json_rpc(
        {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "initialize",
            "params": {"protocolVersion": "1999-01-01"},
        }
    )
    assert response["result"]["protocolVersion"] == DEFAULT_PROTOCOL


def test_initialize_without_protocol_version() -> None:
    response = handle_json_rpc({"jsonrpc": "2.0", "id": 3, "method": "initialize", "params": {}})
    assert response["result"]["protocolVersion"] in SUPPORTED_PROTOCOLS


def test_tools_list_returns_tools() -> None:
    response = handle_json_rpc({"jsonrpc": "2.0", "id": 4, "method": "tools/list"})
    assert response["id"] == 4
    tools = response["result"]["tools"]
    assert isinstance(tools, list)
    assert len(tools) > 0
    assert all("name" in tool for tool in tools)


def test_tools_call_returns_structured_content(minimal_repo: Path) -> None:
    response = handle_json_rpc(
        {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "tools/call",
            "params": {
                "name": "code_explanation",
                "arguments": {"repo": str(minimal_repo), "path": "app.py"},
            },
        }
    )
    assert response["id"] == 5
    assert "structuredContent" in response["result"]
    assert response["result"]["structuredContent"]["feature"] == "code_explanation"


def test_tools_call_with_prefix(minimal_repo: Path) -> None:
    response = handle_json_rpc(
        {
            "jsonrpc": "2.0",
            "id": 6,
            "method": "tools/call",
            "params": {
                "name": "gitlab_code_explanation",
                "arguments": {"repo": str(minimal_repo), "path": "app.py"},
            },
        },
        tool_prefix="gitlab_",
    )
    assert response["result"]["structuredContent"]["feature"] == "code_explanation"


def test_unknown_method_returns_error() -> None:
    response = handle_json_rpc({"jsonrpc": "2.0", "id": 7, "method": "nonexistent/method"})
    assert response["error"]["code"] == -32601
    assert "unknown method" in response["error"]["message"]


def test_tools_call_unknown_tool_returns_error(tmp_path: Path) -> None:
    response = handle_json_rpc(
        {
            "jsonrpc": "2.0",
            "id": 8,
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {"repo": str(tmp_path)},
            },
        }
    )
    assert "error" in response
    assert response["error"]["code"] < 0


def test_tools_call_missing_required_arg_returns_error(tmp_path: Path) -> None:
    response = handle_json_rpc(
        {
            "jsonrpc": "2.0",
            "id": 9,
            "method": "tools/call",
            "params": {
                "name": "code_explanation",
                "arguments": {"repo": str(tmp_path)},
            },
        }
    )
    assert "error" in response


def test_handle_json_rpc_with_missing_params() -> None:
    response = handle_json_rpc({"jsonrpc": "2.0", "id": 10, "method": "tools/list"})
    assert "result" in response


def test_handle_json_rpc_preserves_id() -> None:
    response = handle_json_rpc(
        {"jsonrpc": "2.0", "id": "string-id", "method": "initialize", "params": {}}
    )
    assert response["id"] == "string-id"


def test_handle_json_rpc_with_null_id() -> None:
    response = handle_json_rpc({"jsonrpc": "2.0", "id": None, "method": "initialize", "params": {}})
    assert response["id"] is None
