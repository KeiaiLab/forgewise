from __future__ import annotations

from pathlib import Path

from forgewise.features import ForgeWise


def _sample_repo(tmp_path: Path) -> Path:
    source = tmp_path / "service.py"
    source.write_text(
        "\n".join(
            [
                "import subprocess",
                "",
                "API_TOKEN = 'abc123'",
                "",
                "class BillingService:",
                "    def total(self, prices: list[int]) -> int:",
                "        return sum(prices)",
                "",
                "def run(command: str) -> str:",
                "    return subprocess.check_output(command, shell=True, text=True)",
                "",
                "def unsafe(expr: str) -> object:",
                "    return eval(expr)",
                "",
            ]
        ),
        encoding="utf-8",
    )
    return tmp_path


def test_code_explanation_summarizes_symbols_and_slice(tmp_path: Path) -> None:
    fw = ForgeWise(_sample_repo(tmp_path))

    result = fw.code_explanation("service.py", start=5, end=7)

    assert result["feature"] == "code_explanation"
    assert "BillingService" in result["symbols"]["classes"]
    assert "total" in result["symbols"]["functions"]
    assert result["slice"]["start"] == 5


def test_test_generation_creates_pytest_skeletons_for_python_functions(tmp_path: Path) -> None:
    fw = ForgeWise(_sample_repo(tmp_path))

    result = fw.test_generation("service.py")

    assert "def test_total" in result["content"]
    assert "def test_run" in result["content"]
    assert result["path"].endswith("test_service.py")


def test_security_features_explain_and_resolve_findings(tmp_path: Path) -> None:
    fw = ForgeWise(_sample_repo(tmp_path))

    explanation = fw.vulnerability_explanation("service.py")
    resolution = fw.vulnerability_resolution("service.py")

    rules = {finding["rule_id"] for finding in explanation["findings"]}
    assert {"python-eval", "shell-true", "hardcoded-secret"} <= rules
    assert any("literal_eval" in fix["suggestion"] for fix in resolution["fixes"])
    assert any("shell=True" in fix["before"] for fix in resolution["fixes"])


def test_duo_chat_retrieves_relevant_context_without_external_llm(tmp_path: Path) -> None:
    fw = ForgeWise(_sample_repo(tmp_path))

    result = fw.duo_chat("where is billing total calculated?")

    assert result["feature"] == "duo_chat"
    assert result["matches"]
    assert result["matches"][0]["path"] == "service.py"


def test_summary_generation_features_cover_enterprise_beta_surface(tmp_path: Path) -> None:
    fw = ForgeWise(_sample_repo(tmp_path))

    commit = fw.merge_commit_message_generation()
    review_summary = fw.code_review_summary()
    issue = fw.issue_description_generation("unsafe command execution in billing service")

    assert commit["feature"] == "merge_commit_message_generation"
    assert commit["message"].startswith("chore:")
    assert review_summary["feature"] == "code_review_summary"
    assert review_summary["total_findings"] >= 3
    assert issue["feature"] == "issue_description_generation"
    assert "unsafe command execution" in issue["title"]
    assert "Acceptance Criteria" in issue["body"]
