from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

from forgewise.features import ForgeWise
from forgewise.llm import LLMClient, LLMConfig


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
    ide_result = fw.code_explanation_ide("service.py", start=5, end=7)
    ui_result = fw.code_explanation_gitlab_ui("service.py", start=5, end=7)

    assert result["feature"] == "code_explanation"
    assert "BillingService" in result["symbols"]["classes"]
    assert "total" in result["symbols"]["functions"]
    assert result["slice"]["start"] == 5
    assert ide_result["feature"] == "code_explanation_ide"
    assert ide_result["surface"] == "ide"
    assert ui_result["feature"] == "code_explanation_gitlab_ui"
    assert ui_result["surface"] == "gitlab_ui"


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


# --- LLM 통합 테스트 ---


def _mock_llm(response: str = "AI 응답") -> LLMClient:
    """LLM generate() 가 고정 문자열을 반환하는 Mock."""
    client = LLMClient(LLMConfig(backend="none"))
    mock_generate = MagicMock(return_value=response)
    client.generate = mock_generate  # type: ignore[assignment]
    return client


def test_code_explanation_with_llm_overrides_summary(tmp_path: Path) -> None:
    """LLM 이 활성화되면 summary 필드가 AI 응답으로 대체된다."""
    llm = _mock_llm("이 코드는 BillingService 클래스입니다.")
    fw = ForgeWise(_sample_repo(tmp_path), llm=llm)

    result = fw.code_explanation("service.py", start=5, end=7)

    assert result["summary"] == "이 코드는 BillingService 클래스입니다."
    assert result["symbols"]["classes"]  # 기존 필드 유지


def test_duo_chat_with_llm_overrides_answer(tmp_path: Path) -> None:
    """LLM 이 활성화되면 answer 필드가 AI 응답으로 대체된다."""
    llm = _mock_llm("billing total 은 BillingService.total() 에서 계산됩니다.")
    fw = ForgeWise(_sample_repo(tmp_path), llm=llm)

    result = fw.duo_chat("where is billing total calculated?")

    assert result["answer"] == "billing total 은 BillingService.total() 에서 계산됩니다."
    assert result["matches"]  # 기존 필드 유지


def test_code_review_with_llm_adds_ai_comments(tmp_path: Path) -> None:
    """LLM 이 활성화되면 ai_comments 필드가 추가된다."""
    llm = _mock_llm("eval() 사용은 위험합니다. ast.literal_eval() 을 사용하세요.")
    fw = ForgeWise(_sample_repo(tmp_path), llm=llm)

    result = fw.code_review()

    assert result["findings"]  # 기존 필드 유지
    assert result["ai_comments"] == "eval() 사용은 위험합니다. ast.literal_eval() 을 사용하세요."


def test_root_cause_analysis_with_llm_adds_ai_analysis(tmp_path: Path) -> None:
    """LLM 이 활성화되면 ai_analysis 필드가 추가된다."""
    llm = _mock_llm("근본 원인: 파일 경로가 잘못되었습니다.")
    fw = ForgeWise(_sample_repo(tmp_path), llm=llm)
    log = 'Traceback:\n  File "app.py", line 10\nFileNotFoundError: no such file'

    result = fw.root_cause_analysis(log)

    assert result["error"]  # 기존 필드 유지
    assert result["ai_analysis"] == "근본 원인: 파일 경로가 잘못되었습니다."


def test_merge_request_summary_with_llm_adds_ai_summary(tmp_path: Path) -> None:
    """LLM 이 활성화되면 ai_summary 필드가 추가된다."""
    llm = _mock_llm("이 MR 은 보안 취약점을 수정합니다.")
    fw = ForgeWise(_sample_repo(tmp_path), llm=llm)

    result = fw.merge_request_summary()

    assert result["summary"]  # 기존 필드 유지
    assert result["ai_summary"] == "이 MR 은 보안 취약점을 수정합니다."


def test_merge_commit_message_with_llm_overrides_message(tmp_path: Path) -> None:
    """LLM 이 활성화되면 message 필드가 AI 응답으로 대체된다."""
    llm = _mock_llm("fix(security): eval() 호출 제거")
    fw = ForgeWise(_sample_repo(tmp_path), llm=llm)

    result = fw.merge_commit_message_generation()

    assert result["message"] == "fix(security): eval() 호출 제거"


def test_issue_description_with_llm_overrides_body(tmp_path: Path) -> None:
    """LLM 이 활성화되면 body 필드가 AI 응답으로 대체된다."""
    llm = _mock_llm("## Summary\n보안 취약점 수정\n\n## Acceptance Criteria\n- 테스트 통과")
    fw = ForgeWise(_sample_repo(tmp_path), llm=llm)

    result = fw.issue_description_generation("security fix")

    assert result["body"] == "## Summary\n보안 취약점 수정\n\n## Acceptance Criteria\n- 테스트 통과"
    assert result["title"] == "security fix"  # 기존 필드 유지


def test_llm_failure_preserves_deterministic_result(tmp_path: Path) -> None:
    """LLM generate() 가 빈 문자열 반환 시 기존 결정론적 결과 유지."""
    llm = _mock_llm("")  # LLM 실패 시뮬레이션
    fw = ForgeWise(_sample_repo(tmp_path), llm=llm)

    explanation = fw.code_explanation("service.py", start=5, end=7)
    fw.duo_chat("billing")  # LLM 실패 시에도 예외 없이 동작 확인
    review = fw.code_review()
    issue = fw.issue_description_generation("test issue")
    commit = fw.merge_commit_message_generation()

    # 모두 기존 결정론적 결과와 동일해야 함
    assert "BillingService" in explanation["summary"] or "lines" in explanation["summary"]
    assert "ai_comments" not in review  # 빈 문자열이면 추가 안 됨
    assert "Acceptance Criteria" in issue["body"]
    assert commit["message"].startswith("chore:")
