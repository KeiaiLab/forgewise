"""GitLab REST API v4 클라이언트."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote

import httpx


@dataclass(frozen=True)
class GitLabConfig:
    base_url: str
    token: str
    timeout: float = 10.0

    @classmethod
    def from_arguments(cls, arguments: dict[str, Any]) -> GitLabConfig:
        base_url = str(
            arguments.get("gitlab_base_url") or os.getenv("GITLAB_BASE_URL", "https://gitlab.com")
        )
        token = str(arguments.get("gitlab_token") or os.getenv("GITLAB_TOKEN", ""))
        if not token:
            raise ValueError(
                "GitLab API token이 필요합니다: GITLAB_TOKEN 또는 gitlab_token을 지정하세요."
            )
        timeout_value = arguments.get("gitlab_timeout") or os.getenv("GITLAB_TIMEOUT", "10")
        timeout = float(str(timeout_value))
        return cls(base_url=base_url.rstrip("/"), token=token, timeout=timeout)


class GitLabClient:
    def __init__(self, config: GitLabConfig, http_client: httpx.Client | None = None) -> None:
        self.config = config
        self._http_client = http_client

    def server_version(self) -> dict[str, Any]:
        return {
            "feature": "get_mcp_server_version",
            "name": "forgewise",
            "version": "0.2.0",
            "protocols": ["2025-03-26", "2025-06-18"],
            "transports": ["stdio", "streamable-http"],
        }

    def create_issue(
        self, project_id: str, title: str, description: str | None = None
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"title": title}
        if description:
            payload["description"] = description
        return self._request(
            "create_issue", "POST", f"/projects/{_project(project_id)}/issues", json_data=payload
        )

    def get_issue(self, project_id: str, issue_iid: int) -> dict[str, Any]:
        return self._request(
            "get_issue", "GET", f"/projects/{_project(project_id)}/issues/{issue_iid}"
        )

    def create_merge_request(
        self,
        project_id: str,
        title: str,
        source_branch: str,
        target_branch: str,
        description: str | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "title": title,
            "source_branch": source_branch,
            "target_branch": target_branch,
        }
        if description:
            payload["description"] = description
        return self._request(
            "create_merge_request",
            "POST",
            f"/projects/{_project(project_id)}/merge_requests",
            json_data=payload,
        )

    def get_merge_request(self, project_id: str, merge_request_iid: int) -> dict[str, Any]:
        return self._request(
            "get_merge_request",
            "GET",
            f"/projects/{_project(project_id)}/merge_requests/{merge_request_iid}",
        )

    def get_merge_request_commits(self, project_id: str, merge_request_iid: int) -> dict[str, Any]:
        return self._request(
            "get_merge_request_commits",
            "GET",
            f"/projects/{_project(project_id)}/merge_requests/{merge_request_iid}/commits",
        )

    def get_merge_request_diffs(self, project_id: str, merge_request_iid: int) -> dict[str, Any]:
        return self._request(
            "get_merge_request_diffs",
            "GET",
            f"/projects/{_project(project_id)}/merge_requests/{merge_request_iid}/diffs",
        )

    def get_merge_request_pipelines(
        self, project_id: str, merge_request_iid: int
    ) -> dict[str, Any]:
        return self._request(
            "get_merge_request_pipelines",
            "GET",
            f"/projects/{_project(project_id)}/merge_requests/{merge_request_iid}/pipelines",
        )

    def get_pipeline_jobs(self, project_id: str, pipeline_id: int) -> dict[str, Any]:
        return self._request(
            "get_pipeline_jobs",
            "GET",
            f"/projects/{_project(project_id)}/pipelines/{pipeline_id}/jobs",
        )

    def manage_pipeline(
        self,
        project_id: str,
        operation: str,
        pipeline_id: int | None = None,
        ref: str | None = None,
        variables: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        if operation == "list":
            params = {"ref": ref} if ref else None
            return self._request(
                "manage_pipeline",
                "GET",
                f"/projects/{_project(project_id)}/pipelines",
                params=params,
            )
        if operation == "create" and ref:
            payload: dict[str, Any] = {"ref": ref}
            if variables:
                payload["variables"] = [
                    {"key": key, "value": value} for key, value in sorted(variables.items())
                ]
            return self._request(
                "manage_pipeline",
                "POST",
                f"/projects/{_project(project_id)}/pipeline",
                json_data=payload,
            )
        if operation in {"retry", "cancel"} and pipeline_id is not None:
            return self._request(
                "manage_pipeline",
                "POST",
                f"/projects/{_project(project_id)}/pipelines/{pipeline_id}/{operation}",
            )
        raise ValueError(
            "manage_pipeline은 list, create(ref 필요), retry/cancel(pipeline_id 필요)만 지원합니다."
        )

    def create_workitem_note(
        self, project_id: str, work_item_iid: int, body: str
    ) -> dict[str, Any]:
        return self._request(
            "create_workitem_note",
            "POST",
            f"/projects/{_project(project_id)}/work_items/{work_item_iid}/notes",
            json_data={"body": body},
        )

    def get_workitem_notes(self, project_id: str, work_item_iid: int) -> dict[str, Any]:
        return self._request(
            "get_workitem_notes",
            "GET",
            f"/projects/{_project(project_id)}/work_items/{work_item_iid}/notes",
        )

    def search(
        self,
        scope: str,
        search: str,
        project_id: str | None = None,
        group_id: str | None = None,
    ) -> dict[str, Any]:
        params = {"scope": scope, "search": search}
        if project_id:
            path = f"/projects/{_project(project_id)}/search"
        elif group_id:
            path = f"/groups/{_project(group_id)}/search"
        else:
            path = "/search"
        return self._request("search", "GET", path, params=params)

    def search_labels(
        self,
        search: str | None = None,
        project_id: str | None = None,
        group_id: str | None = None,
    ) -> dict[str, Any]:
        params = {"search": search} if search else None
        if project_id:
            path = f"/projects/{_project(project_id)}/labels"
        elif group_id:
            path = f"/groups/{_project(group_id)}/labels"
        else:
            raise ValueError("search_labels에는 id 또는 group_id가 필요합니다.")
        return self._request("search_labels", "GET", path, params=params)

    def semantic_code_search(self, project_id: str, query: str) -> dict[str, Any]:
        return self._request(
            "semantic_code_search",
            "GET",
            f"/projects/{_project(project_id)}/search/semantic",
            params={"scope": "blobs", "search": query},
        )

    def _request(
        self,
        feature: str,
        method: str,
        path: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.config.base_url}/api/v4{path}"
        headers = {"Authorization": f"Bearer {self.config.token}"}
        own_client = self._http_client is None
        client = self._http_client or httpx.Client(timeout=self.config.timeout)
        try:
            response = client.request(method, url, headers=headers, params=params, json=json_data)
            if response.status_code >= 400:
                message = response.text.replace(self.config.token, "[REDACTED]")
                raise RuntimeError(f"GitLab API request failed: {response.status_code} {message}")
            try:
                data: Any = response.json()
            except ValueError:
                data = response.text
            return {
                "feature": feature,
                "request": {"method": method, "path": path, "params": params or {}},
                "data": data,
            }
        finally:
            if own_client:
                client.close()


def _project(project_id: str) -> str:
    return quote(project_id, safe="")
