from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_github_actions_are_not_present() -> None:
    assert not (ROOT / ".github" / "workflows").exists()


def test_product_docs_capture_name_feature_map_and_references() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    design = (ROOT / "docs" / "design.md").read_text(encoding="utf-8")
    references = (ROOT / "docs" / "references.md").read_text(encoding="utf-8")
    audit = (ROOT / "docs" / "completion-audit.md").read_text(encoding="utf-8")
    security = (ROOT / "docs" / "security.md").read_text(encoding="utf-8")

    assert "ForgeWise" in readme
    assert "GitLab Duo" in design
    assert "code_suggestions" in design
    assert "merge_commit_message_generation" in design
    assert "issue_description_generation" in design
    assert "code_explanation_ide" in design
    assert "code_explanation_gitlab_ui" in design
    assert "/api/v4/mcp" in design
    assert "https://docs.gitlab.com/user/gitlab_duo/feature_summary/" in references
    assert (
        "https://docs.gitlab.com/user/gitlab_duo/model_context_protocol/mcp_server/" in references
    )
    assert "https://modelcontextprotocol.io/specification/2025-06-18/server/tools" in references
    assert "FORGEWISE_ENABLE_MUTATIONS" in security
    assert "Prompt-to-artifact checklist" in audit
    assert "make check" in audit


def test_governance_files_present() -> None:
    """S6 Phase 2: 거버넌스 5종 파일 존재 강제."""
    for name in (
        "SECURITY.md",
        "CONTRIBUTING.md",
        "CODE_OF_CONDUCT.md",
        "CHANGELOG.md",
        "AGENTS.md",
    ):
        assert (ROOT / name).exists(), f"{name} missing"


def test_operational_docs_present() -> None:
    """S6 Phase 4: 운영 문서 4종 존재 강제."""
    for name in ("installation.md", "configuration.md", "api-reference.md", "upgrade.md"):
        assert (ROOT / "docs" / name).exists(), f"docs/{name} missing"


def test_lefthook_yml_present() -> None:
    """S6 Phase 1: lefthook.yml 존재 + setup-hooks target 강제 (RFC-0002 정합)."""
    assert (ROOT / "lefthook.yml").exists()
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "setup-hooks" in makefile


def test_security_md_has_contact_channel() -> None:
    """SECURITY.md 가 보안 신고 채널 + SLO 를 갖춤."""
    security = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "security@keiailab.org" in security
    assert "Security Advisory" in security or "보안 신고" in security
    assert "Response SLO" in security or "SLO" in security


def test_contributing_md_has_dco_and_conventional_commits() -> None:
    """CONTRIBUTING.md 가 DCO + Conventional Commits 정책을 명시."""
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    assert "Signed-off-by" in contributing
    assert "Conventional Commits" in contributing or "Conventional" in contributing
    assert "make check" in contributing
    assert "lefthook" in contributing


def test_code_of_conduct_references_contributor_covenant() -> None:
    """CODE_OF_CONDUCT.md 가 Contributor Covenant 를 외부 참조."""
    coc = (ROOT / "CODE_OF_CONDUCT.md").read_text(encoding="utf-8")
    assert "Contributor Covenant" in coc
    assert "conduct@keiailab.org" in coc


def test_changelog_md_has_unreleased_and_0_1_0() -> None:
    """CHANGELOG.md 가 Keep a Changelog 양식 + [Unreleased] + [0.1.0]."""
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "Keep a Changelog" in changelog
    assert "[Unreleased]" in changelog
    assert "0.1.0" in changelog
    assert "Semantic Versioning" in changelog


def test_agents_md_has_python_override_matrix() -> None:
    """AGENTS.md 가 Tier-3 Python override 매트릭스를 갖춤."""
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "Tier-3" in agents
    assert "Python" in agents
    assert "ruff" in agents
    assert "mypy" in agents
    assert "uv" in agents


def test_installation_md_has_python_version_and_env_table() -> None:
    """docs/installation.md 가 Python 3.11+ 요구 + 환경 변수 표 + troubleshooting."""
    installation = (ROOT / "docs" / "installation.md").read_text(encoding="utf-8")
    assert "Python 3.11" in installation
    assert "uv" in installation
    assert "GITLAB_BASE_URL" in installation
    assert "GITLAB_TOKEN" in installation
    assert "FORGEWISE_ENABLE_MUTATIONS" in installation
    assert "troubleshooting" in installation.lower() or "트러블슈팅" in installation


def test_configuration_md_has_mcp_client_and_oauth_scope() -> None:
    """docs/configuration.md 가 MCP client 등록 + OAuth scope 표."""
    configuration = (ROOT / "docs" / "configuration.md").read_text(encoding="utf-8")
    assert "forgewise-mcp" in configuration
    assert "forgewise-http" in configuration
    assert "OAuth" in configuration
    assert "read_repository" in configuration
    assert "read_api" in configuration
    assert "audit" in configuration.lower()


def test_api_reference_md_has_33_tools() -> None:
    """docs/api-reference.md 가 33 종 MCP tool 카탈로그를 갖춤."""
    api_reference = (ROOT / "docs" / "api-reference.md").read_text(encoding="utf-8")
    # 18 Duo + 15 GitLab compat = 33 종
    duo_tools = (
        "code_suggestions",
        "duo_chat",
        "code_explanation_ide",
        "code_explanation_gitlab_ui",
        "refactor_code",
        "fix_code",
        "test_generation",
        "code_review",
        "root_cause_analysis",
        "vulnerability_explanation",
        "vulnerability_resolution",
        "merge_request_summary",
        "merge_commit_message_generation",
        "code_review_summary",
        "issue_description_generation",
        "discussion_summary",
        "sdlc_trends",
    )
    gitlab_tools = (
        "get_mcp_server_version",
        "create_issue",
        "get_issue",
        "create_merge_request",
        "get_merge_request",
        "get_merge_request_commits",
        "get_merge_request_diffs",
        "get_merge_request_pipelines",
        "get_pipeline_jobs",
        "manage_pipeline",
        "create_workitem_note",
        "get_workitem_notes",
        "search",
        "search_labels",
        "semantic_code_search",
    )
    for tool in duo_tools + gitlab_tools:
        assert tool in api_reference, f"docs/api-reference.md missing {tool}"


def test_upgrade_md_has_semver_policy() -> None:
    """docs/upgrade.md 가 SemVer 정책 + 마이그레이션 template."""
    upgrade = (ROOT / "docs" / "upgrade.md").read_text(encoding="utf-8")
    assert "Semantic Versioning" in upgrade or "SemVer" in upgrade
    assert "0.1.0" in upgrade
    assert "마이그레이션" in upgrade or "migration" in upgrade.lower()
