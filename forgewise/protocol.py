"""MCP JSON-RPC 프로토콜 핸들러."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from forgewise.llm import LLMClient
from forgewise.metrics import record_error, record_tool_call, track_duration
from forgewise.tools import McpToolError, ToolRuntime, call_tool, list_tools

SUPPORTED_PROTOCOLS = ["2025-03-26", "2025-06-18"]
DEFAULT_PROTOCOL = "2025-06-18"


def handle_json_rpc(
    message: dict[str, Any],
    *,
    root: Path | str = ".",
    tool_prefix: str = "",
    gitlab_http_client: httpx.Client | None = None,
    llm: LLMClient | None = None,
) -> dict[str, Any]:
    method = str(message.get("method", ""))
    msg_id = message.get("id")
    if method == "initialize":
        requested = _requested_protocol(message)
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": requested
                if requested in SUPPORTED_PROTOCOLS
                else DEFAULT_PROTOCOL,
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "forgewise", "version": "0.2.0"},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": list_tools(prefix=tool_prefix)}}
    if method == "tools/call":
        return _handle_tool_call(msg_id, message, Path(root), tool_prefix, gitlab_http_client, llm)
    return _error(msg_id, -32601, f"unknown method: {method}")


def _handle_tool_call(
    msg_id: Any,
    message: dict[str, Any],
    root: Path,
    tool_prefix: str,
    gitlab_http_client: httpx.Client | None,
    llm: LLMClient | None,
) -> dict[str, Any]:
    params = _dict(message.get("params"))
    raw_name = str(params.get("name", ""))
    name = _strip_prefix(raw_name, tool_prefix)
    arguments = _dict(params.get("arguments"))
    runtime = ToolRuntime(root=root.resolve(), gitlab_http_client=gitlab_http_client, llm=llm)

    record_tool_call(name)
    with track_duration():
        try:
            result = call_tool(name, arguments, runtime)
        except McpToolError as exc:
            record_error("mcp_tool_error")
            return _error(msg_id, exc.code, str(exc))
        except (RuntimeError, ValueError) as exc:
            record_error("runtime_error")
            return _error(msg_id, -32602, str(exc))

    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, sort_keys=True),
                }
            ],
            "structuredContent": result,
        },
    }


def _requested_protocol(message: dict[str, Any]) -> str:
    params = _dict(message.get("params"))
    return str(params.get("protocolVersion") or DEFAULT_PROTOCOL)


def _strip_prefix(name: str, prefix: str) -> str:
    if prefix and name.startswith(prefix):
        return name[len(prefix) :]
    return name


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _error(msg_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}
