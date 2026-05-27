from __future__ import annotations

import json
from pathlib import Path

from forgewise.audit import _redact, write_audit


def test_write_audit_creates_jsonl_record(tmp_path: Path) -> None:
    args = {"repo": "/tmp/r", "path": "a.py"}
    write_audit(tmp_path, "code_explanation", args, {"feature": "code_explanation"})

    audit_file = tmp_path / ".forgewise" / "audit.jsonl"
    assert audit_file.exists()
    record = json.loads(audit_file.read_text(encoding="utf-8").strip())
    assert record["tool"] == "code_explanation"
    assert record["feature"] == "code_explanation"
    assert "at" in record


def test_write_audit_appends_multiple_records(tmp_path: Path) -> None:
    write_audit(tmp_path, "tool_a", {}, {"feature": "a"})
    write_audit(tmp_path, "tool_b", {}, {"feature": "b"})

    audit = tmp_path / ".forgewise" / "audit.jsonl"
    lines = audit.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[0])["tool"] == "tool_a"
    assert json.loads(lines[1])["tool"] == "tool_b"


def test_write_audit_redacts_sensitive_arguments(tmp_path: Path) -> None:
    write_audit(
        tmp_path,
        "get_issue",
        {"token": "super-secret", "project": "my-project"},
        {"feature": "get_issue"},
    )

    record = json.loads(
        (tmp_path / ".forgewise" / "audit.jsonl").read_text(encoding="utf-8").strip()
    )
    assert record["arguments"]["token"] == "[REDACTED]"
    assert record["arguments"]["project"] == "my-project"


def test_redact_masks_token_key_secret_password() -> None:
    data = {
        "api_token": "abc",
        "secret_key": "xyz",
        "password": "p@ss",
        "normal": "visible",
    }
    result = _redact(data)
    assert result["api_token"] == "[REDACTED]"
    assert result["secret_key"] == "[REDACTED]"
    assert result["password"] == "[REDACTED]"
    assert result["normal"] == "visible"


def test_redact_handles_nested_dicts() -> None:
    data = {"outer": {"inner_token": "hidden", "safe": "ok"}}
    result = _redact(data)
    assert result["outer"]["inner_token"] == "[REDACTED]"
    assert result["outer"]["safe"] == "ok"


def test_redact_handles_lists() -> None:
    data = {"items": [{"key": "hidden"}, {"name": "visible"}]}
    result = _redact(data)
    assert result["items"][0]["key"] == "[REDACTED]"
    assert result["items"][1]["name"] == "visible"


def test_redact_passes_through_scalars() -> None:
    assert _redact("hello") == "hello"
    assert _redact(42) == 42
    assert _redact(None) is None
