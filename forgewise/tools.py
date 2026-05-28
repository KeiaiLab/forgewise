"""MCP 도구 카탈로그 — 33종 도구 정의 및 디스패치."""

from __future__ import annotations

import os
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast

import httpx

from forgewise.audit import write_audit
from forgewise.features import ForgeWise
from forgewise.gitlab_client import GitLabClient, GitLabConfig

ToolHandler = Callable[["ToolRuntime", dict[str, Any]], dict[str, Any]]


class McpToolError(ValueError):
    def __init__(self, message: str, code: int = -32602) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ToolRuntime:
    root: Path
    gitlab_http_client: httpx.Client | None = None


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    properties: dict[str, Any]
    required: list[str]
    handler: ToolHandler
    annotations: dict[str, Any] = field(default_factory=dict)
    accepts_repo: bool = True

    def to_dict(self, prefix: str = "") -> dict[str, Any]:
        properties = dict(self.properties)
        if self.accepts_repo:
            properties = {
                "repo": _string_schema("저장소 루트 경로. 생략 시 서버 기본 경로를 사용합니다."),
                **properties,
            }
        result = {
            "name": f"{prefix}{self.name}",
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": self.required,
            },
        }
        if self.annotations:
            result["annotations"] = self.annotations
        return result


def list_tool_definitions() -> list[ToolDefinition]:
    return [
        _local_tool(
            "code_suggestions",
            "저장소 전체의 코드 개선 후보를 찾습니다.",
            {},
            lambda fw, args: fw.code_suggestions(),
        ),
        _local_tool(
            "duo_chat",
            "질문과 관련된 로컬 코드 문맥을 검색합니다.",
            {"question": _string_schema("질문")},
            lambda fw, args: fw.duo_chat(str(args["question"])),
            ["question"],
        ),
        _local_tool(
            "code_explanation",
            "파일 또는 라인 범위를 설명하는 호환 alias입니다.",
            _path_schema(),
            _explain("code_explanation"),
            ["path"],
        ),
        _local_tool(
            "code_explanation_ide",
            "IDE 코드 설명 행에 대응하는 설명을 반환합니다.",
            _path_schema(),
            _explain("code_explanation_ide"),
            ["path"],
        ),
        _local_tool(
            "code_explanation_gitlab_ui",
            "GitLab UI 코드 설명 행에 대응하는 설명을 반환합니다.",
            _path_schema(),
            _explain("code_explanation_gitlab_ui"),
            ["path"],
        ),
        _local_tool(
            "refactor_code",
            "리팩터링 후보를 반환합니다.",
            _path_schema(),
            lambda fw, args: fw.refactor_code(str(args["path"])),
            ["path"],
        ),
        _local_tool(
            "fix_code",
            "자동 수정 가능한 위험 후보를 제안합니다.",
            _path_schema(),
            lambda fw, args: fw.fix_code(str(args["path"])),
            ["path"],
        ),
        _local_tool(
            "test_generation",
            "Python 함수에 대한 pytest skeleton을 생성합니다.",
            _path_schema(),
            lambda fw, args: fw.test_generation(str(args["path"])),
            ["path"],
        ),
        _local_tool(
            "code_review",
            "보안과 유지보수성 중심 리뷰를 수행합니다.",
            {},
            lambda fw, args: fw.code_review(),
        ),
        _local_tool(
            "root_cause_analysis",
            "스택트레이스에서 원인 후보를 추출합니다.",
            {"log": _string_schema("로그 경로 또는 로그 본문")},
            lambda fw, args: fw.root_cause_analysis(str(args["log"])),
            ["log"],
        ),
        _local_tool(
            "vulnerability_explanation",
            "취약 패턴을 설명합니다.",
            _path_schema(),
            lambda fw, args: fw.vulnerability_explanation(str(args["path"])),
            ["path"],
        ),
        _local_tool(
            "vulnerability_resolution",
            "취약 패턴 수정 방향을 제시합니다.",
            _path_schema(),
            lambda fw, args: fw.vulnerability_resolution(str(args["path"])),
            ["path"],
        ),
        _local_tool(
            "merge_request_summary",
            "git diff 통계를 MR 요약으로 바꿉니다.",
            {"base": _string_schema("비교 기준 ref")},
            lambda fw, args: fw.merge_request_summary(str(args.get("base", "HEAD~1"))),
        ),
        _local_tool(
            "merge_commit_message_generation",
            "git diff 통계를 merge commit message로 바꿉니다.",
            {"base": _string_schema("비교 기준 ref")},
            lambda fw, args: fw.merge_commit_message_generation(str(args.get("base", "HEAD~1"))),
        ),
        _local_tool(
            "code_review_summary",
            "코드 리뷰 finding을 요약합니다.",
            {},
            lambda fw, args: fw.code_review_summary(),
        ),
        _local_tool(
            "issue_description_generation",
            "이슈 설명 초안을 생성합니다.",
            {"prompt": _string_schema("이슈 프롬프트")},
            lambda fw, args: fw.issue_description_generation(str(args["prompt"])),
            ["prompt"],
        ),
        _local_tool(
            "discussion_summary",
            "토론 텍스트를 요약합니다.",
            {"text": _string_schema("토론 본문")},
            lambda fw, args: fw.discussion_summary(str(args["text"])),
            ["text"],
        ),
        _local_tool(
            "sdlc_trends",
            "언어 분포와 품질 finding 수를 집계합니다.",
            {},
            lambda fw, args: fw.sdlc_trends(),
        ),
        _gitlab_tool(
            "get_mcp_server_version",
            "ForgeWise MCP 서버 버전과 지원 protocol을 반환합니다.",
            {},
            _server_version,
            accepts_repo=False,
        ),
        _gitlab_tool(
            "create_issue",
            "GitLab issue를 생성합니다.",
            {
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "title": _string_schema("이슈 제목"),
                "description": _string_schema("이슈 설명"),
            },
            _create_issue,
            ["id", "title"],
            mutating=True,
        ),
        _gitlab_tool(
            "get_issue",
            "GitLab issue를 조회합니다.",
            {
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "issue_iid": _integer_schema("이슈 IID"),
            },
            _get_issue,
            ["id", "issue_iid"],
        ),
        _gitlab_tool(
            "create_merge_request",
            "GitLab merge request를 생성합니다.",
            {
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "title": _string_schema("MR 제목"),
                "source_branch": _string_schema("source branch"),
                "target_branch": _string_schema("target branch"),
                "description": _string_schema("MR 설명"),
            },
            _create_merge_request,
            ["id", "title", "source_branch", "target_branch"],
            mutating=True,
        ),
        _gitlab_tool(
            "get_merge_request",
            "GitLab merge request를 조회합니다.",
            {
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "merge_request_iid": _integer_schema("MR IID"),
            },
            _get_merge_request,
            ["id", "merge_request_iid"],
        ),
        _gitlab_tool(
            "get_merge_request_commits",
            "MR commit 목록을 조회합니다.",
            {
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "merge_request_iid": _integer_schema("MR IID"),
            },
            _get_merge_request_commits,
            ["id", "merge_request_iid"],
        ),
        _gitlab_tool(
            "get_merge_request_diffs",
            "MR diff 목록을 조회합니다.",
            {
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "merge_request_iid": _integer_schema("MR IID"),
            },
            _get_merge_request_diffs,
            ["id", "merge_request_iid"],
        ),
        _gitlab_tool(
            "get_merge_request_pipelines",
            "MR pipeline 목록을 조회합니다.",
            {
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "merge_request_iid": _integer_schema("MR IID"),
            },
            _get_merge_request_pipelines,
            ["id", "merge_request_iid"],
        ),
        _gitlab_tool(
            "get_pipeline_jobs",
            "Pipeline job 목록을 조회합니다.",
            {
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "pipeline_id": _integer_schema("Pipeline ID"),
            },
            _get_pipeline_jobs,
            ["id", "pipeline_id"],
        ),
        _gitlab_tool(
            "manage_pipeline",
            "Pipeline list/create/retry/cancel을 수행합니다.",
            {
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "operation": _string_schema("list, create, retry, cancel"),
                "pipeline_id": _integer_schema("Pipeline ID"),
                "ref": _string_schema("branch 또는 tag ref"),
                "variables": {"type": "object", "additionalProperties": {"type": "string"}},
            },
            _manage_pipeline,
            ["id", "operation"],
            mutating=True,
        ),
        _gitlab_tool(
            "create_workitem_note",
            "Work item note를 생성합니다.",
            {
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "work_item_iid": _integer_schema("Work item IID"),
                "body": _string_schema("note 본문"),
            },
            _create_workitem_note,
            ["id", "work_item_iid", "body"],
            mutating=True,
        ),
        _gitlab_tool(
            "get_workitem_notes",
            "Work item note 목록을 조회합니다.",
            {
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "work_item_iid": _integer_schema("Work item IID"),
            },
            _get_workitem_notes,
            ["id", "work_item_iid"],
        ),
        _gitlab_tool(
            "search",
            "GitLab search API를 호출합니다.",
            {
                "scope": _string_schema("검색 scope"),
                "search": _string_schema("검색어"),
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "group_id": _string_schema("그룹 ID 또는 full path"),
            },
            _search,
            ["scope", "search"],
        ),
        _gitlab_tool(
            "search_labels",
            "GitLab label을 검색합니다.",
            {
                "search": _string_schema("검색어"),
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "group_id": _string_schema("그룹 ID 또는 full path"),
            },
            _search_labels,
        ),
        _gitlab_tool(
            "semantic_code_search",
            "GitLab semantic code search를 호출합니다.",
            {
                "id": _string_schema("프로젝트 ID 또는 full path"),
                "query": _string_schema("검색 질의"),
            },
            _semantic_code_search,
            ["id", "query"],
        ),
    ]


def list_tools(prefix: str = "") -> list[dict[str, Any]]:
    return [tool.to_dict(prefix=prefix) for tool in list_tool_definitions()]


def call_tool(name: str, arguments: dict[str, Any], runtime: ToolRuntime) -> dict[str, Any]:
    normalized = name
    tools = {tool.name: tool for tool in list_tool_definitions()}
    if normalized not in tools:
        raise McpToolError(f"unknown tool: {name}")
    tool = tools[normalized]
    _validate_schema(tool, arguments)
    root = _resolve_root(runtime.root, arguments)
    child_runtime = ToolRuntime(root=root, gitlab_http_client=runtime.gitlab_http_client)
    result = tool.handler(child_runtime, dict(arguments))
    write_audit(root, name, arguments, result)
    return result


def _validate_required(tool: ToolDefinition, arguments: dict[str, Any]) -> None:
    missing = [key for key in tool.required if key not in arguments or arguments[key] in (None, "")]
    if missing:
        raise McpToolError(f"필수 인자가 없습니다: {', '.join(missing)}")


# JSON Schema type -> Python 타입 매핑 (경량 검증용)
_JSON_TYPE_MAP: dict[str, tuple[type, ...]] = {
    "string": (str,),
    "integer": (int,),
    "number": (int, float),
    "boolean": (bool,),
    "object": (dict,),
}


def _validate_schema(tool: ToolDefinition, arguments: dict[str, Any]) -> None:
    """inputSchema 의 required + type 제약을 검증한다.

    외부 의존성 없이 경량으로 구현한다.
    실패 시 JSON-RPC -32602 (Invalid params) McpToolError 를 발생시킨다.
    """
    # 1) required 검증
    _validate_required(tool, arguments)

    # 2) type 검증 -- 선언된 properties 에 값이 존재할 때만 검사
    properties = tool.properties
    for key, value in arguments.items():
        if key not in properties:
            continue
        prop_schema = properties[key]
        declared_type = prop_schema.get("type")
        if declared_type is None or value is None:
            continue
        expected = _JSON_TYPE_MAP.get(declared_type)
        if expected is None:
            continue
        # JSON 에서 bool 은 int 의 하위 클래스이므로 integer/number 일 때 bool 은 거부
        if declared_type in ("integer", "number") and isinstance(value, bool):
            raise McpToolError(
                f"인자 '{key}' 의 타입이 올바르지 않습니다: 기대={declared_type}, 실제=boolean"
            )
        if not isinstance(value, expected):
            actual = type(value).__name__
            raise McpToolError(
                f"인자 '{key}' 의 타입이 올바르지 않습니다: 기대={declared_type}, 실제={actual}"
            )


def _resolve_root(default_root: Path, arguments: dict[str, Any]) -> Path:
    value = arguments.get("repo")
    return Path(str(value)).resolve() if value else default_root.resolve()


def _local_tool(
    name: str,
    description: str,
    properties: dict[str, Any],
    feature_handler: Callable[[ForgeWise, dict[str, Any]], dict[str, Any]],
    required: list[str] | None = None,
) -> ToolDefinition:
    def handler(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
        return feature_handler(ForgeWise(runtime.root), args)

    return ToolDefinition(
        name=name,
        description=description,
        properties=properties,
        required=[] if required is None else required,
        handler=handler,
        annotations={"readOnlyHint": True},
    )


def _gitlab_tool(
    name: str,
    description: str,
    properties: dict[str, Any],
    handler: ToolHandler,
    required: list[str] | None = None,
    *,
    accepts_repo: bool = True,
    mutating: bool = False,
) -> ToolDefinition:
    annotations = {"readOnlyHint": not mutating, "destructiveHint": False}
    if mutating:
        annotations["openWorldHint"] = True
    return ToolDefinition(
        name=name,
        description=description,
        properties={**_gitlab_connection_schema(), **properties},
        required=[] if required is None else required,
        handler=handler,
        annotations=annotations,
        accepts_repo=accepts_repo,
    )


def _explain(feature: str) -> Callable[[ForgeWise, dict[str, Any]], dict[str, Any]]:
    def handler(fw: ForgeWise, args: dict[str, Any]) -> dict[str, Any]:
        method = cast(
            Callable[[str, int | None, int | None], dict[str, Any]],
            getattr(fw, feature),
        )
        return method(
            str(args["path"]), _optional_int(args.get("start")), _optional_int(args.get("end"))
        )

    return handler


def _server_version(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    return GitLabClient(
        GitLabConfig(base_url="https://gitlab.com", token="unused"),  # noqa: S106
        runtime.gitlab_http_client,
    ).server_version()


def _create_issue(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    _require_mutations()
    return _client(runtime, args).create_issue(
        str(args["id"]), str(args["title"]), _optional_str(args.get("description"))
    )


def _get_issue(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    return _client(runtime, args).get_issue(str(args["id"]), int(args["issue_iid"]))


def _create_merge_request(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    _require_mutations()
    return _client(runtime, args).create_merge_request(
        str(args["id"]),
        str(args["title"]),
        str(args["source_branch"]),
        str(args["target_branch"]),
        _optional_str(args.get("description")),
    )


def _get_merge_request(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    return _client(runtime, args).get_merge_request(str(args["id"]), int(args["merge_request_iid"]))


def _get_merge_request_commits(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    return _client(runtime, args).get_merge_request_commits(
        str(args["id"]), int(args["merge_request_iid"])
    )


def _get_merge_request_diffs(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    return _client(runtime, args).get_merge_request_diffs(
        str(args["id"]), int(args["merge_request_iid"])
    )


def _get_merge_request_pipelines(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    return _client(runtime, args).get_merge_request_pipelines(
        str(args["id"]), int(args["merge_request_iid"])
    )


def _get_pipeline_jobs(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    return _client(runtime, args).get_pipeline_jobs(str(args["id"]), int(args["pipeline_id"]))


def _manage_pipeline(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    if str(args["operation"]) != "list":
        _require_mutations()
    raw_variables = args.get("variables")
    variables = raw_variables if isinstance(raw_variables, dict) else None
    return _client(runtime, args).manage_pipeline(
        str(args["id"]),
        str(args["operation"]),
        _optional_int(args.get("pipeline_id")),
        _optional_str(args.get("ref")),
        variables,
    )


def _create_workitem_note(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    _require_mutations()
    return _client(runtime, args).create_workitem_note(
        str(args["id"]), int(args["work_item_iid"]), str(args["body"])
    )


def _get_workitem_notes(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    return _client(runtime, args).get_workitem_notes(str(args["id"]), int(args["work_item_iid"]))


def _search(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    return _client(runtime, args).search(
        str(args["scope"]),
        str(args["search"]),
        _optional_str(args.get("id")),
        _optional_str(args.get("group_id")),
    )


def _search_labels(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    return _client(runtime, args).search_labels(
        _optional_str(args.get("search")),
        _optional_str(args.get("id")),
        _optional_str(args.get("group_id")),
    )


def _semantic_code_search(runtime: ToolRuntime, args: dict[str, Any]) -> dict[str, Any]:
    return _client(runtime, args).semantic_code_search(str(args["id"]), str(args["query"]))


def _client(runtime: ToolRuntime, args: dict[str, Any]) -> GitLabClient:
    try:
        config = GitLabConfig.from_arguments(args)
    except ValueError as exc:
        raise McpToolError(str(exc)) from exc
    return GitLabClient(config, runtime.gitlab_http_client)


def _require_mutations() -> None:
    if os.getenv("FORGEWISE_ENABLE_MUTATIONS") != "1":
        raise McpToolError("변경성 GitLab tool은 FORGEWISE_ENABLE_MUTATIONS=1일 때만 실행됩니다.")


def _gitlab_connection_schema() -> dict[str, Any]:
    return {
        "gitlab_base_url": _string_schema(
            "GitLab base URL. 기본값은 GITLAB_BASE_URL 또는 https://gitlab.com"
        ),
        "gitlab_token": _string_schema("GitLab API token. 기본값은 GITLAB_TOKEN"),
        "gitlab_timeout": {
            "type": "number",
            "description": "GitLab API timeout seconds (하위 호환: connect/read 양쪽 적용)",
        },
        "gitlab_connect_timeout": {
            "type": "number",
            "description": "GitLab API connect timeout seconds. 기본값 5초",
        },
        "gitlab_read_timeout": {
            "type": "number",
            "description": "GitLab API read timeout seconds. 기본값 30초",
        },
    }


def _string_schema(description: str) -> dict[str, Any]:
    return {"type": "string", "description": description}


def _integer_schema(description: str) -> dict[str, Any]:
    return {"type": "integer", "description": description, "minimum": 1}


def _path_schema() -> dict[str, Any]:
    return {
        "path": _string_schema("저장소 루트 기준 파일 경로"),
        "start": {"type": "integer", "description": "시작 라인", "minimum": 1},
        "end": {"type": "integer", "description": "종료 라인", "minimum": 1},
    }


def _optional_int(value: Any) -> int | None:
    return int(value) if value is not None else None


def _optional_str(value: Any) -> str | None:
    return str(value) if value not in (None, "") else None
