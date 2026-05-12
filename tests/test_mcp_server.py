from __future__ import annotations

import json
from pathlib import Path

from forgewise.mcp_server import handle_json_rpc, list_tools


def test_mcp_lists_gitlab_duo_mapped_tools() -> None:
    tool_names = {tool["name"] for tool in list_tools()}

    assert {
        "code_suggestions",
        "duo_chat",
        "code_explanation",
        "refactor_code",
        "fix_code",
        "test_generation",
        "code_review",
        "root_cause_analysis",
        "vulnerability_explanation",
        "vulnerability_resolution",
        "merge_request_summary",
        "discussion_summary",
        "sdlc_trends",
        "merge_commit_message_generation",
        "code_review_summary",
        "issue_description_generation",
    } <= tool_names


def test_mcp_tool_call_returns_structured_content_and_audit_log(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text(
        "def add(a: int, b: int) -> int:\n    return a + b\n",
        encoding="utf-8",
    )
    request = {
        "jsonrpc": "2.0",
        "id": 7,
        "method": "tools/call",
        "params": {
            "name": "code_explanation",
            "arguments": {"repo": str(tmp_path), "path": "app.py"},
        },
    }

    response = handle_json_rpc(request)

    assert response["id"] == 7
    assert response["result"]["structuredContent"]["feature"] == "code_explanation"
    assert response["result"]["content"][0]["type"] == "text"
    audit = tmp_path / ".forgewise" / "audit.jsonl"
    assert audit.exists()
    first_record = json.loads(audit.read_text(encoding="utf-8").splitlines()[0])
    assert first_record["tool"] == "code_explanation"
