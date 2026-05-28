"""E2E 테스트: 실 GitLab CE 인스턴스 연동.

FORGEWISE_E2E=1 환경변수가 설정된 경우에만 실행됩니다.
GitLab CE 인스턴스는 docker-compose.e2e.yml 로 로컬 구동합니다.

필요 환경변수:
    FORGEWISE_E2E=1          — E2E 테스트 활성화
    GITLAB_TOKEN             — GitLab API token
    GITLAB_BASE_URL          — GitLab CE base URL (기본: http://localhost:9080)
    FORGEWISE_E2E_PROJECT_ID — 테스트 프로젝트 ID (기본: root/forgewise-e2e-test)

실행:
    FORGEWISE_E2E=1 GITLAB_TOKEN=e2e-test-token GITLAB_BASE_URL=http://localhost:9080 \\
        uv run --extra dev python -m pytest tests/test_e2e_gitlab.py -v
"""

from __future__ import annotations

import os

import pytest

from forgewise.gitlab_client import GitLabClient, GitLabConfig

# ---------------------------------------------------------------------------
# E2E 환경 감지
# ---------------------------------------------------------------------------

E2E_ENABLED = os.getenv("FORGEWISE_E2E") == "1"

pytestmark = [
    pytest.mark.e2e,
    pytest.mark.skipif(not E2E_ENABLED, reason="FORGEWISE_E2E=1 미설정 — E2E 건너뜀"),
]


# ---------------------------------------------------------------------------
# Fixtures (session scope — GitLab CE 부팅 비용 최소화)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def gitlab_config() -> GitLabConfig:
    """실 GitLab CE 인스턴스 접속 설정."""
    base_url = os.getenv("GITLAB_BASE_URL", "http://localhost:9080")
    token = os.getenv("GITLAB_TOKEN", "")
    if not token:
        pytest.fail("GITLAB_TOKEN 환경변수가 필요합니다.")
    return GitLabConfig(base_url=base_url, token=token, timeout=30.0)


@pytest.fixture(scope="session")
def gitlab_client(gitlab_config: GitLabConfig) -> GitLabClient:
    """세션 수명의 GitLabClient (실 HTTP 호출)."""
    return GitLabClient(gitlab_config)


@pytest.fixture(scope="session")
def e2e_project_id() -> str:
    """테스트 대상 프로젝트 ID."""
    return os.getenv("FORGEWISE_E2E_PROJECT_ID", "root/forgewise-e2e-test")


# ---------------------------------------------------------------------------
# E2E 테스트: 최소 5개 GitLab compat tool 호출 검증
# ---------------------------------------------------------------------------


class TestE2EGitLabListProjects:
    """search(scope='projects') 로 프로젝트 목록 조회."""

    def test_search_projects_returns_list(
        self, gitlab_client: GitLabClient, e2e_project_id: str
    ) -> None:
        result = gitlab_client.search(
            scope="projects",
            search="forgewise",
        )

        assert result["feature"] == "search"
        assert isinstance(result["data"], list)


class TestE2EGitLabGetProject:
    """search_labels 로 프로젝트 접근성 확인 (get_project 대용)."""

    def test_search_labels_confirms_project_access(
        self, gitlab_client: GitLabClient, e2e_project_id: str
    ) -> None:
        result = gitlab_client.search_labels(project_id=e2e_project_id)

        assert result["feature"] == "search_labels"
        # data 는 list (라벨이 없어도 빈 list)
        assert isinstance(result["data"], list)


class TestE2EGitLabListIssues:
    """search(scope='issues') 로 이슈 목록 조회."""

    def test_search_issues_returns_list(
        self, gitlab_client: GitLabClient, e2e_project_id: str
    ) -> None:
        result = gitlab_client.search(
            scope="issues",
            search="E2E",
            project_id=e2e_project_id,
        )

        assert result["feature"] == "search"
        assert isinstance(result["data"], list)


class TestE2EGitLabCreateIssue:
    """create_issue 로 이슈 생성 후 get_issue 로 확인."""

    def test_create_and_get_issue(
        self, gitlab_client: GitLabClient, e2e_project_id: str
    ) -> None:
        # 생성
        created = gitlab_client.create_issue(
            project_id=e2e_project_id,
            title="ForgeWise E2E 자동 생성 이슈",
            description="test_e2e_gitlab.py 에서 자동 생성된 이슈입니다.",
        )

        assert created["feature"] == "create_issue"
        assert "iid" in created["data"]
        issue_iid: int = created["data"]["iid"]

        # 조회
        fetched = gitlab_client.get_issue(
            project_id=e2e_project_id,
            issue_iid=issue_iid,
        )

        assert fetched["feature"] == "get_issue"
        assert fetched["data"]["iid"] == issue_iid
        assert fetched["data"]["title"] == "ForgeWise E2E 자동 생성 이슈"


class TestE2EGitLabSearchBlobs:
    """search(scope='blobs') 로 코드 검색."""

    def test_search_blobs_finds_code(
        self, gitlab_client: GitLabClient, e2e_project_id: str
    ) -> None:
        result = gitlab_client.search(
            scope="blobs",
            search="ForgeWise",
            project_id=e2e_project_id,
        )

        assert result["feature"] == "search"
        assert isinstance(result["data"], list)


class TestE2EGitLabServerVersion:
    """get_mcp_server_version 호출 검증 (네트워크 불필요, 통합 검증)."""

    def test_server_version_returns_metadata(
        self, gitlab_client: GitLabClient
    ) -> None:
        result = gitlab_client.server_version()

        assert result["feature"] == "get_mcp_server_version"
        assert result["name"] == "forgewise"
        assert "version" in result


class TestE2EGitLabWorkitemNotes:
    """create_issue → create_workitem_note → get_workitem_notes 흐름."""

    def test_create_and_list_workitem_notes(
        self, gitlab_client: GitLabClient, e2e_project_id: str
    ) -> None:
        # 이슈 생성 (work item note 대상)
        issue = gitlab_client.create_issue(
            project_id=e2e_project_id,
            title="E2E workitem note 테스트 이슈",
        )
        issue_iid: int = issue["data"]["iid"]

        # note 생성
        note = gitlab_client.create_workitem_note(
            project_id=e2e_project_id,
            work_item_iid=issue_iid,
            body="E2E 테스트 노트입니다.",
        )

        assert note["feature"] == "create_workitem_note"

        # note 목록 조회
        notes = gitlab_client.get_workitem_notes(
            project_id=e2e_project_id,
            work_item_iid=issue_iid,
        )

        assert notes["feature"] == "get_workitem_notes"
