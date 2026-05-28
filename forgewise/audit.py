"""MCP 도구 호출 감사 로그 기록."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

#: audit.jsonl 최대 크기 (바이트). 환경변수 FORGEWISE_AUDIT_MAX_BYTES 로 재정의 가능.
DEFAULT_MAX_BYTES: int = 10_485_760  # 10 MB

#: rotation 보관 파일 최대 수. 환경변수 FORGEWISE_AUDIT_MAX_FILES 로 재정의 가능.
DEFAULT_MAX_FILES: int = 5

_AUDIT_FILENAME = "audit.jsonl"


def _get_max_bytes() -> int:
    """환경변수에서 최대 바이트 수를 읽는다."""
    raw = os.environ.get("FORGEWISE_AUDIT_MAX_BYTES")
    if raw is not None:
        return int(raw)
    return DEFAULT_MAX_BYTES


def _get_max_files() -> int:
    """환경변수에서 최대 rotation 파일 수를 읽는다."""
    raw = os.environ.get("FORGEWISE_AUDIT_MAX_FILES")
    if raw is not None:
        return int(raw)
    return DEFAULT_MAX_FILES


def _rotate(audit_path: Path, max_files: int) -> None:
    """기존 audit 파일들을 한 단계씩 뒤로 밀어 rotation 수행.

    audit.jsonl -> audit.jsonl.1 -> audit.jsonl.2 -> ...
    max_files 를 초과하는 가장 오래된 파일은 삭제한다.
    """
    for i in range(max_files, 0, -1):
        src = audit_path.parent / f"{_AUDIT_FILENAME}.{i}"
        if not src.exists():
            continue
        if i >= max_files:
            src.unlink()
        else:
            dst = audit_path.parent / f"{_AUDIT_FILENAME}.{i + 1}"
            src.rename(dst)

    if audit_path.exists():
        audit_path.rename(audit_path.parent / f"{_AUDIT_FILENAME}.1")


def write_audit(
    root: Path,
    tool: str,
    arguments: dict[str, Any],
    result: dict[str, Any],
    *,
    _max_bytes: int | None = None,
    _max_files: int | None = None,
) -> None:
    """감사 로그 한 건을 audit.jsonl 에 기록한다.

    파일 크기가 max_bytes 를 초과하면 자동으로 rotation 을 수행한다.
    """
    audit_dir = root / ".forgewise"
    audit_dir.mkdir(exist_ok=True)

    audit_path = audit_dir / _AUDIT_FILENAME
    max_bytes = _max_bytes if _max_bytes is not None else _get_max_bytes()
    max_files = _max_files if _max_files is not None else _get_max_files()

    if audit_path.exists() and audit_path.stat().st_size >= max_bytes:
        _rotate(audit_path, max_files)

    record = {
        "at": datetime.now(UTC).isoformat(),
        "tool": tool,
        "arguments": _redact(arguments),
        "feature": result.get("feature"),
    }
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")


def _redact(value: Any) -> Any:
    """민감 키(key, token, secret, password)를 마스킹한다."""
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
