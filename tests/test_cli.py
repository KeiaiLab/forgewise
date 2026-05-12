from __future__ import annotations

from pathlib import Path

import pytest

from forgewise.cli import main


def test_cli_explain_prints_json(capsys: pytest.CaptureFixture[str], tmp_path: Path) -> None:
    (tmp_path / "calc.py").write_text(
        "def add(a: int, b: int) -> int:\n    return a + b\n",
        encoding="utf-8",
    )

    code = main(["--repo", str(tmp_path), "explain", "calc.py"])

    captured = capsys.readouterr()
    assert code == 0
    assert '"feature": "code_explanation"' in captured.out


def test_cli_check_runs_review_and_security(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    (tmp_path / "unsafe.py").write_text("value = eval('1 + 1')\n", encoding="utf-8")

    code = main(["--repo", str(tmp_path), "check"])

    captured = capsys.readouterr()
    assert code == 1
    assert "python-eval" in captured.out


def test_cli_issue_description_prints_json(
    capsys: pytest.CaptureFixture[str], tmp_path: Path
) -> None:
    code = main(["--repo", str(tmp_path), "issue-description", "login failure after deploy"])

    captured = capsys.readouterr()
    assert code == 0
    assert '"feature": "issue_description_generation"' in captured.out
