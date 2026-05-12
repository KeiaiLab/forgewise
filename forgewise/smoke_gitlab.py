from __future__ import annotations

import os

from forgewise.gitlab_client import GitLabClient, GitLabConfig


def main() -> int:
    base_url = str(
        os.getenv("FORGEWISE_LIVE_GITLAB_URL") or os.getenv("GITLAB_BASE_URL", "https://gitlab.com")
    )
    token = os.getenv("FORGEWISE_LIVE_GITLAB_TOKEN") or os.getenv("GITLAB_TOKEN")
    project_id = os.getenv("FORGEWISE_LIVE_PROJECT_ID")
    if not token or not project_id:
        print(
            "live GitLab smoke skipped: "
            "FORGEWISE_LIVE_GITLAB_TOKEN/GITLAB_TOKEN과 "
            "FORGEWISE_LIVE_PROJECT_ID가 필요합니다."
        )
        return 0

    client = GitLabClient(GitLabConfig(base_url=base_url, token=token))
    version = client.server_version()
    labels = client.search_labels(project_id=project_id)
    count = len(labels["data"]) if isinstance(labels["data"], list) else "unknown"
    print(f"server={version['name']} version={version['version']}")
    print(f"gitlab_project={project_id} label_count={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
