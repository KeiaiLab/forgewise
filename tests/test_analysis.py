from __future__ import annotations

from pathlib import Path

from forgewise import analysis
from forgewise.analysis import (
    language_trends,
    python_symbols,
    refactor_suggestions,
    retrieve_context,
)
from forgewise.repository import Repository


def test_python_symbols_extracts_classes_functions_imports() -> None:
    code = "\n".join(
        [
            "import os",
            "from pathlib import Path",
            "",
            "class Foo:",
            "    pass",
            "",
            "def bar() -> None:",
            "    pass",
            "",
            "async def baz() -> None:",
            "    pass",
        ]
    )
    symbols = python_symbols(code)
    assert "Foo" in symbols["classes"]
    assert "bar" in symbols["functions"]
    assert "baz" in symbols["functions"]
    assert "os" in symbols["imports"]
    assert "pathlib" in symbols["imports"]


def test_python_symbols_returns_empty_on_syntax_error() -> None:
    symbols = python_symbols("def broken(:\n")
    assert symbols == {"classes": [], "functions": [], "imports": []}


def test_python_symbols_deduplicates_and_sorts() -> None:
    code = "def alpha(): pass\ndef alpha(): pass\ndef beta(): pass\n"
    symbols = python_symbols(code)
    assert symbols["functions"] == ["alpha", "beta"]


def test_refactor_suggestions_detects_long_lines() -> None:
    long_line = "x = " + "a" * 120
    suggestions = refactor_suggestions("test.py", long_line)
    assert any(s.rule_id == "long-line" for s in suggestions)


def test_refactor_suggestions_detects_bare_except() -> None:
    code = "try:\n    pass\nexcept:\n    pass\n"
    suggestions = refactor_suggestions("test.py", code)
    assert any(s.rule_id == "bare-except" for s in suggestions)


def test_refactor_suggestions_detects_large_function() -> None:
    lines = ["def big_func():"] + ["    x = 1"] * 55
    code = "\n".join(lines)
    suggestions = refactor_suggestions("test.py", code)
    assert any(s.rule_id == "large-function" for s in suggestions)


def test_refactor_suggestions_handles_syntax_error() -> None:
    suggestions = refactor_suggestions("test.py", "def broken(:\n")
    assert isinstance(suggestions, list)


def test_test_skeleton_generates_pytest_functions() -> None:
    code = "def hello(): pass\ndef world(): pass\ndef _private(): pass\n"
    path, content = analysis.test_skeleton_for_python("module.py", code)
    assert path == "tests/test_module.py"
    assert "def test_hello" in content
    assert "def test_world" in content
    assert "_private" not in content


def test_test_skeleton_fallback_for_no_public_functions() -> None:
    code = "def _internal(): pass\n"
    _, content = analysis.test_skeleton_for_python("module.py", code)
    assert "def test_module_imports" in content


def test_retrieve_context_finds_matching_files(sample_repo: Path) -> None:
    repo = Repository(sample_repo)
    matches = retrieve_context(repo, "BillingService total")
    assert len(matches) >= 1
    assert matches[0]["path"] == "service.py"
    assert matches[0]["score"] > 0


def test_retrieve_context_returns_empty_for_no_match(tmp_path: Path) -> None:
    (tmp_path / "empty.py").write_text("x = 1\n", encoding="utf-8")
    repo = Repository(tmp_path)
    matches = retrieve_context(repo, "zzz_nonexistent_symbol")
    assert matches == []


def test_retrieve_context_respects_limit(sample_repo: Path) -> None:
    repo = Repository(sample_repo)
    matches = retrieve_context(repo, "def", limit=1)
    assert len(matches) <= 1


def test_language_trends_counts_file_extensions(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("x = 1\n", encoding="utf-8")
    (tmp_path / "b.py").write_text("y = 2\n", encoding="utf-8")
    (tmp_path / "c.js").write_text("var z = 3;\n", encoding="utf-8")
    repo = Repository(tmp_path)
    trends = language_trends(repo)
    assert trends["files"] == 3
    assert trends["languages"]["py"] == 2
    assert trends["languages"]["js"] == 1
