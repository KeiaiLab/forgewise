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
