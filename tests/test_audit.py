"""audit.py -- 감사 로그 기록 및 rotation 로직 단위 테스트."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from forgewise.audit import (
    _AUDIT_FILENAME,
    DEFAULT_MAX_BYTES,
    DEFAULT_MAX_FILES,
    _redact,
    _rotate,
    write_audit,
)


# ---------------------------------------------------------------------------
# 헬퍼
# ---------------------------------------------------------------------------


def _make_result(feature: str = "test") -> dict[str, Any]:
    return {"feature": feature}


def _write_n(root: Path, n: int, *, max_bytes: int, max_files: int) -> None:
    """헬퍼: *n* 건의 감사 로그를 기록한다."""
    for i in range(n):
        write_audit(
            root,
            f"tool_{i}",
            {"arg": i},
            _make_result(),
            _max_bytes=max_bytes,
            _max_files=max_files,
        )


# ---------------------------------------------------------------------------
# 기본 기록 (main 에서 머지된 기존 테스트)
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# _rotate 단위 테스트
# ---------------------------------------------------------------------------


class TestRotate:
    """_rotate 함수의 파일 이동/삭제 동작을 검증한다."""

    def test_empty_dir(self, tmp_path: Path) -> None:
        """rotation 대상 파일이 없을 때 오류 없이 동작한다."""
        audit_path = tmp_path / _AUDIT_FILENAME
        _rotate(audit_path, max_files=5)
        assert not audit_path.exists()

    def test_single_file(self, tmp_path: Path) -> None:
        """기존 audit.jsonl 1개만 있을 때 .1 로 rename 된다."""
        audit_path = tmp_path / _AUDIT_FILENAME
        audit_path.write_text("line\n")
        _rotate(audit_path, max_files=5)
        assert not audit_path.exists()
        assert (tmp_path / f"{_AUDIT_FILENAME}.1").exists()

    def test_cascading(self, tmp_path: Path) -> None:
        """기존 .1, .2 가 있으면 .2->.3, .1->.2, audit.jsonl->.1 로 cascade."""
        audit_path = tmp_path / _AUDIT_FILENAME
        audit_path.write_text("current\n")
        (tmp_path / f"{_AUDIT_FILENAME}.1").write_text("old1\n")
        (tmp_path / f"{_AUDIT_FILENAME}.2").write_text("old2\n")

        _rotate(audit_path, max_files=5)

        assert not audit_path.exists()
        assert (tmp_path / f"{_AUDIT_FILENAME}.1").read_text() == "current\n"
        assert (tmp_path / f"{_AUDIT_FILENAME}.2").read_text() == "old1\n"
        assert (tmp_path / f"{_AUDIT_FILENAME}.3").read_text() == "old2\n"

    def test_deletes_at_max(self, tmp_path: Path) -> None:
        """max_files 에 도달한 파일은 삭제된다."""
        audit_path = tmp_path / _AUDIT_FILENAME
        audit_path.write_text("current\n")
        (tmp_path / f"{_AUDIT_FILENAME}.1").write_text("old1\n")
        (tmp_path / f"{_AUDIT_FILENAME}.2").write_text("old2\n")

        _rotate(audit_path, max_files=2)

        assert not audit_path.exists()
        assert (tmp_path / f"{_AUDIT_FILENAME}.1").read_text() == "current\n"
        assert (tmp_path / f"{_AUDIT_FILENAME}.2").read_text() == "old1\n"
        # old2 는 max_files=2 초과이므로 삭제
        assert not (tmp_path / f"{_AUDIT_FILENAME}.3").exists()


# ---------------------------------------------------------------------------
# rotation 통합 테스트
# ---------------------------------------------------------------------------


class TestRotationIntegration:
    """write_audit 를 통한 rotation 통합 동작을 검증한다."""

    def test_creates_numbered_backup(self, tmp_path: Path) -> None:
        """크기 초과 시 기존 파일이 .1 으로 rename 되고 새 파일이 생긴다."""
        max_bytes = 100
        _write_n(tmp_path, 20, max_bytes=max_bytes, max_files=5)

        audit_dir = tmp_path / ".forgewise"
        assert (audit_dir / _AUDIT_FILENAME).exists()
        assert (audit_dir / f"{_AUDIT_FILENAME}.1").exists()

    def test_cascades_numbers(self, tmp_path: Path) -> None:
        """rotation 이 연속으로 발생하면 .1 -> .2 -> .3 순으로 cascade 된다."""
        max_bytes = 50
        _write_n(tmp_path, 10, max_bytes=max_bytes, max_files=5)

        audit_dir = tmp_path / ".forgewise"
        rotated = sorted(audit_dir.glob(f"{_AUDIT_FILENAME}.*"))
        assert len(rotated) >= 2, f"rotated 파일이 2개 이상이어야 한다: {rotated}"

    def test_deletes_oldest(self, tmp_path: Path) -> None:
        """max_files 를 초과하면 가장 오래된 파일이 삭제된다."""
        max_bytes = 50
        max_files = 3
        _write_n(tmp_path, 30, max_bytes=max_bytes, max_files=max_files)

        audit_dir = tmp_path / ".forgewise"
        rotated = sorted(audit_dir.glob(f"{_AUDIT_FILENAME}.*"))
        for p in rotated:
            suffix_num = int(p.name.split(".")[-1])
            assert suffix_num <= max_files, (
                f"{p.name}: 번호 {suffix_num} > max_files {max_files}"
            )

    def test_max_files_limit(self, tmp_path: Path) -> None:
        """rotation 파일 총 수가 max_files 를 초과하지 않는다."""
        max_bytes = 50
        max_files = 2
        _write_n(tmp_path, 50, max_bytes=max_bytes, max_files=max_files)

        audit_dir = tmp_path / ".forgewise"
        rotated = list(audit_dir.glob(f"{_AUDIT_FILENAME}.*"))
        assert len(rotated) <= max_files

    def test_current_file_stays_small(self, tmp_path: Path) -> None:
        """rotation 후 현재 파일은 max_bytes 미만이어야 한다."""
        max_bytes = 200
        _write_n(tmp_path, 50, max_bytes=max_bytes, max_files=5)

        audit_path = tmp_path / ".forgewise" / _AUDIT_FILENAME
        # 마지막 기록 직후이므로 현재 파일은 max_bytes 미만이어야 한다
        # (한 레코드 추가 후이므로 약간의 여유는 있다)
        assert audit_path.stat().st_size < max_bytes * 2


# ---------------------------------------------------------------------------
# 환경변수 연동
# ---------------------------------------------------------------------------


class TestEnvironmentVariables:
    """환경변수로 설정값을 재정의하는 동작을 검증한다."""

    def test_env_max_bytes(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """FORGEWISE_AUDIT_MAX_BYTES 환경변수가 적용된다."""
        monkeypatch.setenv("FORGEWISE_AUDIT_MAX_BYTES", "200")
        # _max_bytes 를 명시하지 않으면 환경변수 값이 사용됨
        for i in range(20):
            write_audit(tmp_path, f"t_{i}", {"x": i}, _make_result())

        audit_dir = tmp_path / ".forgewise"
        # 200바이트 기준이면 여러 레코드 후 rotation 발생해야 한다
        rotated = list(audit_dir.glob(f"{_AUDIT_FILENAME}.*"))
        assert len(rotated) >= 1

    def test_env_max_files(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """FORGEWISE_AUDIT_MAX_FILES 환경변수가 적용된다."""
        monkeypatch.setenv("FORGEWISE_AUDIT_MAX_FILES", "2")
        monkeypatch.setenv("FORGEWISE_AUDIT_MAX_BYTES", "50")
        for i in range(30):
            write_audit(tmp_path, f"t_{i}", {"x": i}, _make_result())

        audit_dir = tmp_path / ".forgewise"
        rotated = list(audit_dir.glob(f"{_AUDIT_FILENAME}.*"))
        assert len(rotated) <= 2


# ---------------------------------------------------------------------------
# 기본값 상수 확인
# ---------------------------------------------------------------------------


class TestDefaults:
    """기본값 상수가 이슈 명세와 일치하는지 검증한다."""

    def test_default_max_bytes(self) -> None:
        assert DEFAULT_MAX_BYTES == 10_485_760  # 10 MB

    def test_default_max_files(self) -> None:
        assert DEFAULT_MAX_FILES == 5
