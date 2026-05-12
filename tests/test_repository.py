from __future__ import annotations

from pathlib import Path

from forgewise.repository import Repository, line_slice


def test_repository_scans_text_files_and_ignores_generated_dirs(tmp_path: Path) -> None:
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("def hello():\n    return 'hi'\n", encoding="utf-8")
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("secret", encoding="utf-8")
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "__pycache__" / "app.pyc").write_bytes(b"\x00\x01")

    repo = Repository(tmp_path)

    assert [path.as_posix() for path in repo.iter_files()] == ["src/app.py"]
    assert repo.read_text(Path("src/app.py")).startswith("def hello")


def test_line_slice_uses_one_based_inclusive_ranges() -> None:
    text = "one\ntwo\nthree\nfour\n"

    assert line_slice(text, start=2, end=3) == "two\nthree"
