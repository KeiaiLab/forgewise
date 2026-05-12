from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def write_audit(root: Path, tool: str, arguments: dict[str, Any], result: dict[str, Any]) -> None:
    audit_dir = root / ".forgewise"
    audit_dir.mkdir(exist_ok=True)
    record = {
        "at": datetime.now(UTC).isoformat(),
        "tool": tool,
        "arguments": _redact(arguments),
        "feature": result.get("feature"),
    }
    with (audit_dir / "audit.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        redacted: dict[str, Any] = {}
        for key, child in value.items():
            if any(token in key.lower() for token in ("key", "token", "secret", "password")):
                redacted[key] = "[REDACTED]"
            else:
                redacted[key] = _redact(child)
        return redacted
    if isinstance(value, list):
        return [_redact(child) for child in value]
    return value
