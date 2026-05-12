from __future__ import annotations

import json
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any, BinaryIO

from forgewise.audit import write_audit
from forgewise.features import ForgeWise

ToolHandler = Callable[[ForgeWise, dict[str, Any]], dict[str, Any]]


def _string_schema(description: str) -> dict[str, Any]:
    return {"type": "string", "description": description}


def list_tools() -> list[dict[str, Any]]:
    return [
        _tool("code_suggestions", "저장소 전체의 코드 개선 후보를 찾습니다.", {}),
        _tool(
            "duo_chat",
            "질문과 관련된 로컬 코드 문맥을 검색합니다.",
            {"question": _string_schema("질문")},
        ),
        _tool("code_explanation", "파일 또는 라인 범위를 설명합니다.", _path_schema()),
        _tool("refactor_code", "리팩터링 후보를 반환합니다.", _path_schema()),
        _tool("fix_code", "자동 수정 가능한 위험 후보를 제안합니다.", _path_schema()),
        _tool(
            "test_generation",
            "Python 함수에 대한 pytest skeleton을 생성합니다.",
            _path_schema(),
        ),
        _tool("code_review", "보안과 유지보수성 중심 리뷰를 수행합니다.", {}),
        _tool(
            "root_cause_analysis",
            "스택트레이스에서 원인 후보를 추출합니다.",
            {"log": _string_schema("로그 경로 또는 로그 본문")},
        ),
        _tool("vulnerability_explanation", "취약 패턴을 설명합니다.", _path_schema()),
        _tool("vulnerability_resolution", "취약 패턴 수정 방향을 제시합니다.", _path_schema()),
        _tool(
            "merge_request_summary",
            "git diff 통계를 MR 요약으로 바꿉니다.",
            {"base": _string_schema("비교 기준 ref")},
        ),
        _tool(
            "discussion_summary",
            "토론 텍스트를 요약합니다.",
            {"text": _string_schema("토론 본문")},
        ),
        _tool("sdlc_trends", "언어 분포와 품질 finding 수를 집계합니다.", {}),
    ]


def handle_json_rpc(message: dict[str, Any]) -> dict[str, Any]:
    method = str(message.get("method", ""))
    msg_id = message.get("id")
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": msg_id,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "forgewise", "version": "0.1.0"},
            },
        }
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": msg_id, "result": {"tools": list_tools()}}
    if method == "tools/call":
        return _handle_tool_call(msg_id, message)
    return _error(msg_id, -32601, f"unknown method: {method}")


def main() -> int:
    while True:
        payload = _read_content_length_message(sys.stdin.buffer)
        if payload is None:
            return 0
        response = handle_json_rpc(json.loads(payload))
        _write_content_length_message(sys.stdout.buffer, json.dumps(response, ensure_ascii=False))
        sys.stdout.flush()


def _handle_tool_call(msg_id: Any, message: dict[str, Any]) -> dict[str, Any]:
    params = _dict(message.get("params"))
    name = str(params.get("name", ""))
    arguments = _dict(params.get("arguments"))
    root = Path(str(arguments.pop("repo", "."))).resolve()
    fw = ForgeWise(root)
    handlers = _handlers()
    if name not in handlers:
        return _error(msg_id, -32602, f"unknown tool: {name}")
    result = handlers[name](fw, arguments)
    write_audit(root, name, arguments, result)
    return {
        "jsonrpc": "2.0",
        "id": msg_id,
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(result, ensure_ascii=False, sort_keys=True),
                }
            ],
            "structuredContent": result,
        },
    }


def _handlers() -> dict[str, ToolHandler]:
    return {
        "code_suggestions": lambda fw, args: fw.code_suggestions(),
        "duo_chat": lambda fw, args: fw.duo_chat(str(args["question"])),
        "code_explanation": lambda fw, args: fw.code_explanation(
            str(args["path"]), _optional_int(args.get("start")), _optional_int(args.get("end"))
        ),
        "refactor_code": lambda fw, args: fw.refactor_code(str(args["path"])),
        "fix_code": lambda fw, args: fw.fix_code(str(args["path"])),
        "test_generation": lambda fw, args: fw.test_generation(str(args["path"])),
        "code_review": lambda fw, args: fw.code_review(),
        "root_cause_analysis": lambda fw, args: fw.root_cause_analysis(str(args["log"])),
        "vulnerability_explanation": lambda fw, args: fw.vulnerability_explanation(
            str(args["path"])
        ),
        "vulnerability_resolution": lambda fw, args: fw.vulnerability_resolution(
            str(args["path"])
        ),
        "merge_request_summary": lambda fw, args: fw.merge_request_summary(
            str(args.get("base", "HEAD~1"))
        ),
        "discussion_summary": lambda fw, args: fw.discussion_summary(str(args["text"])),
        "sdlc_trends": lambda fw, args: fw.sdlc_trends(),
    }


def _tool(name: str, description: str, properties: dict[str, Any]) -> dict[str, Any]:
    props = {"repo": _string_schema("저장소 루트 경로")}
    props.update(properties)
    required = ["repo", *properties.keys()]
    return {
        "name": name,
        "description": description,
        "inputSchema": {"type": "object", "properties": props, "required": required},
    }


def _path_schema() -> dict[str, Any]:
    return {
        "path": _string_schema("저장소 루트 기준 파일 경로"),
        "start": {"type": "integer", "description": "시작 라인", "minimum": 1},
        "end": {"type": "integer", "description": "종료 라인", "minimum": 1},
    }


def _dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _optional_int(value: Any) -> int | None:
    return int(value) if value is not None else None


def _error(msg_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}


def _read_content_length_message(stream: BinaryIO) -> str | None:
    headers: dict[str, str] = {}
    while True:
        raw = stream.readline()
        if raw == b"":
            return None
        line = raw.decode("ascii", errors="replace").strip()
        if not line:
            break
        key, _, value = line.partition(":")
        headers[key.lower()] = value.strip()
    length = int(headers.get("content-length", "0"))
    if length <= 0:
        return None
    return stream.read(length).decode("utf-8")


def _write_content_length_message(stream: BinaryIO, payload: str) -> None:
    data = payload.encode("utf-8")
    stream.write(f"Content-Length: {len(data)}\r\n\r\n".encode("ascii") + data)
