from __future__ import annotations

import pytest

from forgewise.smoke_gitlab import main


def test_gitlab_smoke_skips_without_live_env(
    capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("FORGEWISE_LIVE_GITLAB_TOKEN", raising=False)
    monkeypatch.delenv("GITLAB_TOKEN", raising=False)
    monkeypatch.delenv("FORGEWISE_LIVE_PROJECT_ID", raising=False)

    code = main()

    captured = capsys.readouterr()
    assert code == 0
    assert "skipped" in captured.out
