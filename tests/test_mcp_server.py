from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from forgewise.mcp_server import (
    _read_content_length_message,
    _write_content_length_message,
    handle_json_rpc,
    list_tools,
    main,
)


def test_mcp_lists_gitlab_duo_mapped_tools() -> None:
    tool_names = {tool["name"] for tool in list_tools()}

    assert {
        "code_suggestions",
        "duo_chat",
        "code_explanation",
        "code_explanation_ide",
        "code_explanation_gitlab_ui",
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


def test_mcp_lists_gitlab_server_compatible_tools() -> None:
    tool_names = {tool["name"] for tool in list_tools()}

    assert {
        "get_mcp_server_version",
        "create_issue",
        "get_issue",
        "create_merge_request",
        "get_merge_request",
        "get_merge_request_commits",
        "get_merge_request_diffs",
        "get_merge_request_pipelines",
        "get_pipeline_jobs",
        "manage_pipeline",
        "create_workitem_note",
        "get_workitem_notes",
        "search",
        "search_labels",
        "semantic_code_search",
    } <= tool_names


def test_mcp_code_explanation_surfaces_are_separate(tmp_path: Path) -> None:
    (tmp_path / "app.py").write_text(
        "def add(a: int, b: int) -> int:\n    return a + b\n",
        encoding="utf-8",
    )
    request = {
        "jsonrpc": "2.0",
        "id": 8,
        "method": "tools/call",
        "params": {
            "name": "code_explanation_gitlab_ui",
            "arguments": {"repo": str(tmp_path), "path": "app.py"},
        },
    }

    response = handle_json_rpc(request)

    assert response["result"]["structuredContent"]["feature"] == "code_explanation_gitlab_ui"
    assert response["result"]["structuredContent"]["surface"] == "gitlab_ui"


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


def test_mcp_tool_prefix_is_accepted_for_calls(tmp_path: Path) -> None:
    request = {
        "jsonrpc": "2.0",
        "id": 9,
        "method": "tools/call",
        "params": {
            "name": "gitlab_get_mcp_server_version",
            "arguments": {"repo": str(tmp_path)},
        },
    }

    response = handle_json_rpc(request, tool_prefix="gitlab_")

    assert response["result"]["structuredContent"]["feature"] == "get_mcp_server_version"


# ─── LSP-style Content-Length transport tests (Phase E3' — mcp_server.py coverage 30% → 70%+) ───


def test_read_content_length_message_parses_valid_payload() -> None:
    raw = b"Content-Length: 5\r\n\r\nhello"
    stream = io.BytesIO(raw)
    assert _read_content_length_message(stream) == "hello"


def test_read_content_length_message_returns_none_on_eof() -> None:
    stream = io.BytesIO(b"")
    assert _read_content_length_message(stream) is None


def test_read_content_length_message_returns_none_when_length_missing() -> None:
    # 헤더 블록 만 (Content-Length 부재) → length 0 → None
    raw = b"\r\n"
    stream = io.BytesIO(raw)
    assert _read_content_length_message(stream) is None


def test_read_content_length_message_handles_multibyte_utf8() -> None:
    # 한국어 + emoji = multibyte UTF-8 payload — byte length 와 char length 다름
    payload = '{"msg":"안녕 🚀"}'
    encoded = payload.encode("utf-8")
    raw = f"Content-Length: {len(encoded)}\r\n\r\n".encode("ascii") + encoded
    stream = io.BytesIO(raw)
    assert _read_content_length_message(stream) == payload


def test_write_content_length_message_emits_lsp_framing() -> None:
    stream = io.BytesIO()
    payload = '{"jsonrpc":"2.0","id":1}'
    _write_content_length_message(stream, payload)
    out = stream.getvalue()
    # Content-Length 헤더 + \r\n\r\n 분리자 + UTF-8 body
    expected_len = len(payload.encode("utf-8"))
    assert out.startswith(f"Content-Length: {expected_len}\r\n\r\n".encode("ascii"))
    assert out.endswith(payload.encode("utf-8"))


def test_main_loop_processes_message_and_returns_on_eof(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    # main(): stdin frame read → handle_json_rpc → stdout write → loop → EOF return 0
    request = {
        "jsonrpc": "2.0",
        "id": 100,
        "method": "tools/list",
    }
    body = json.dumps(request).encode("utf-8")
    in_buffer = io.BytesIO(f"Content-Length: {len(body)}\r\n\r\n".encode("ascii") + body)
    out_buffer = io.BytesIO()

    import sys

    class _FakeStdin:
        buffer = in_buffer

    class _FakeStdout:
        buffer = out_buffer

        @staticmethod
        def flush() -> None:
            pass

    monkeypatch.setattr(sys, "stdin", _FakeStdin())
    monkeypatch.setattr(sys, "stdout", _FakeStdout())

    rc = main()
    assert rc == 0
    raw_out = out_buffer.getvalue()
    # 응답 frame 안 에 tools/list 결과 ("tools" key) 가 있어야 함
    assert b"Content-Length: " in raw_out
    body_start = raw_out.index(b"\r\n\r\n") + 4
    response = json.loads(raw_out[body_start:].decode("utf-8"))
    assert response["id"] == 100
    assert "tools" in response["result"]
