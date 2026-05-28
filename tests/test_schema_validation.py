"""MCP tool inputSchema validation 테스트 — required + type 검증."""

from __future__ import annotations

from pathlib import Path

import pytest

from forgewise.tools import (
    McpToolError,
    ToolDefinition,
    ToolRuntime,
    _validate_schema,
    call_tool,
)


def _noop_handler(runtime: ToolRuntime, args: dict) -> dict:
    """테스트용 no-op handler."""
    return {"ok": True}


def _make_tool(
    *,
    properties: dict | None = None,
    required: list[str] | None = None,
) -> ToolDefinition:
    """테스트용 ToolDefinition 생성 헬퍼."""
    return ToolDefinition(
        name="test_tool",
        description="테스트 도구",
        properties=properties or {},
        required=required or [],
        handler=_noop_handler,
        accepts_repo=False,
    )


# ---------------------------------------------------------------------------
# required 검증
# ---------------------------------------------------------------------------


class TestRequiredValidation:
    """required 필드 누락 시 McpToolError(-32602) 발생 확인."""

    def test_required_field_missing_raises(self) -> None:
        tool = _make_tool(
            properties={"name": {"type": "string"}},
            required=["name"],
        )
        with pytest.raises(McpToolError, match="필수 인자가 없습니다: name") as exc_info:
            _validate_schema(tool, {})
        assert exc_info.value.code == -32602

    def test_required_field_none_raises(self) -> None:
        tool = _make_tool(
            properties={"name": {"type": "string"}},
            required=["name"],
        )
        with pytest.raises(McpToolError, match="필수 인자가 없습니다"):
            _validate_schema(tool, {"name": None})

    def test_required_field_empty_string_raises(self) -> None:
        tool = _make_tool(
            properties={"name": {"type": "string"}},
            required=["name"],
        )
        with pytest.raises(McpToolError, match="필수 인자가 없습니다"):
            _validate_schema(tool, {"name": ""})

    def test_multiple_required_fields_missing(self) -> None:
        tool = _make_tool(
            properties={
                "id": {"type": "string"},
                "title": {"type": "string"},
            },
            required=["id", "title"],
        )
        with pytest.raises(McpToolError, match="id.*title"):
            _validate_schema(tool, {})

    def test_required_field_present_passes(self) -> None:
        tool = _make_tool(
            properties={"name": {"type": "string"}},
            required=["name"],
        )
        # 예외 없이 통과해야 함
        _validate_schema(tool, {"name": "hello"})


# ---------------------------------------------------------------------------
# type 검증 — string
# ---------------------------------------------------------------------------


class TestStringTypeValidation:
    """string 타입 선언 시 비문자열 인자 거부."""

    def test_string_accepts_string(self) -> None:
        tool = _make_tool(properties={"q": {"type": "string"}})
        _validate_schema(tool, {"q": "검색어"})

    def test_string_rejects_integer(self) -> None:
        tool = _make_tool(properties={"q": {"type": "string"}})
        with pytest.raises(McpToolError, match="기대=string.*실제=int") as exc_info:
            _validate_schema(tool, {"q": 42})
        assert exc_info.value.code == -32602

    def test_string_rejects_boolean(self) -> None:
        tool = _make_tool(properties={"q": {"type": "string"}})
        with pytest.raises(McpToolError, match="기대=string.*실제=bool"):
            _validate_schema(tool, {"q": True})

    def test_string_rejects_list(self) -> None:
        tool = _make_tool(properties={"q": {"type": "string"}})
        with pytest.raises(McpToolError, match="기대=string.*실제=list"):
            _validate_schema(tool, {"q": ["a", "b"]})


# ---------------------------------------------------------------------------
# type 검증 — integer
# ---------------------------------------------------------------------------


class TestIntegerTypeValidation:
    """integer 타입 선언 시 비정수 인자 거부."""

    def test_integer_accepts_int(self) -> None:
        tool = _make_tool(properties={"iid": {"type": "integer"}})
        _validate_schema(tool, {"iid": 42})

    def test_integer_rejects_string(self) -> None:
        tool = _make_tool(properties={"iid": {"type": "integer"}})
        with pytest.raises(McpToolError, match="기대=integer.*실제=str"):
            _validate_schema(tool, {"iid": "not-a-number"})

    def test_integer_rejects_float(self) -> None:
        tool = _make_tool(properties={"iid": {"type": "integer"}})
        with pytest.raises(McpToolError, match="기대=integer.*실제=float"):
            _validate_schema(tool, {"iid": 3.14})

    def test_integer_rejects_boolean(self) -> None:
        """Python 에서 bool 은 int 하위 클래스이므로 명시적 거부 확인."""
        tool = _make_tool(properties={"iid": {"type": "integer"}})
        with pytest.raises(McpToolError, match="기대=integer.*실제=boolean"):
            _validate_schema(tool, {"iid": True})


# ---------------------------------------------------------------------------
# type 검증 — number
# ---------------------------------------------------------------------------


class TestNumberTypeValidation:
    """number 타입 선언 시 int/float 모두 허용, 비수치 거부."""

    def test_number_accepts_int(self) -> None:
        tool = _make_tool(properties={"timeout": {"type": "number"}})
        _validate_schema(tool, {"timeout": 30})

    def test_number_accepts_float(self) -> None:
        tool = _make_tool(properties={"timeout": {"type": "number"}})
        _validate_schema(tool, {"timeout": 1.5})

    def test_number_rejects_string(self) -> None:
        tool = _make_tool(properties={"timeout": {"type": "number"}})
        with pytest.raises(McpToolError, match="기대=number.*실제=str"):
            _validate_schema(tool, {"timeout": "fast"})

    def test_number_rejects_boolean(self) -> None:
        tool = _make_tool(properties={"timeout": {"type": "number"}})
        with pytest.raises(McpToolError, match="기대=number.*실제=boolean"):
            _validate_schema(tool, {"timeout": False})


# ---------------------------------------------------------------------------
# type 검증 — boolean
# ---------------------------------------------------------------------------


class TestBooleanTypeValidation:
    """boolean 타입 선언 시 비불리언 거부."""

    def test_boolean_accepts_true(self) -> None:
        tool = _make_tool(properties={"flag": {"type": "boolean"}})
        _validate_schema(tool, {"flag": True})

    def test_boolean_accepts_false(self) -> None:
        tool = _make_tool(properties={"flag": {"type": "boolean"}})
        _validate_schema(tool, {"flag": False})

    def test_boolean_rejects_int(self) -> None:
        tool = _make_tool(properties={"flag": {"type": "boolean"}})
        with pytest.raises(McpToolError, match="기대=boolean.*실제=int"):
            _validate_schema(tool, {"flag": 1})

    def test_boolean_rejects_string(self) -> None:
        tool = _make_tool(properties={"flag": {"type": "boolean"}})
        with pytest.raises(McpToolError, match="기대=boolean.*실제=str"):
            _validate_schema(tool, {"flag": "true"})


# ---------------------------------------------------------------------------
# type 검증 — object
# ---------------------------------------------------------------------------


class TestObjectTypeValidation:
    """object 타입 선언 시 비딕셔너리 거부."""

    def test_object_accepts_dict(self) -> None:
        tool = _make_tool(properties={"vars": {"type": "object"}})
        _validate_schema(tool, {"vars": {"key": "val"}})

    def test_object_rejects_list(self) -> None:
        tool = _make_tool(properties={"vars": {"type": "object"}})
        with pytest.raises(McpToolError, match="기대=object.*실제=list"):
            _validate_schema(tool, {"vars": [1, 2]})

    def test_object_rejects_string(self) -> None:
        tool = _make_tool(properties={"vars": {"type": "object"}})
        with pytest.raises(McpToolError, match="기대=object.*실제=str"):
            _validate_schema(tool, {"vars": "{}"})


# ---------------------------------------------------------------------------
# None 값 / 미선언 키 / 미선언 type — 스킵 경로
# ---------------------------------------------------------------------------


class TestSkipPaths:
    """검증 대상이 아닌 경우 무시하는지 확인."""

    def test_none_value_skips_type_check(self) -> None:
        """None 은 type 검사 대상이 아님."""
        tool = _make_tool(properties={"q": {"type": "string"}})
        _validate_schema(tool, {"q": None})

    def test_unknown_key_skips_type_check(self) -> None:
        """properties 에 없는 키는 무시."""
        tool = _make_tool(properties={"q": {"type": "string"}})
        _validate_schema(tool, {"unknown_key": 999})

    def test_property_without_type_skips(self) -> None:
        """type 선언이 없는 property 는 검증 스킵."""
        tool = _make_tool(properties={"q": {"description": "no type"}})
        _validate_schema(tool, {"q": 42})

    def test_no_properties_no_required(self) -> None:
        """빈 tool 은 어떤 인자든 통과."""
        tool = _make_tool()
        _validate_schema(tool, {"anything": [1, 2, 3]})


# ---------------------------------------------------------------------------
# call_tool 통합 — JSON-RPC -32602 에러 반환
# ---------------------------------------------------------------------------


class TestCallToolValidation:
    """call_tool 경유 시 validation 에러가 McpToolError(-32602) 로 전파되는지 확인."""

    def test_call_tool_required_missing_raises(self, tmp_path: Path) -> None:
        """duo_chat 은 'question' 이 required — 빠뜨리면 에러."""
        runtime = ToolRuntime(root=tmp_path)
        with pytest.raises(McpToolError, match="필수 인자가 없습니다: question") as exc_info:
            call_tool("duo_chat", {"repo": str(tmp_path)}, runtime)
        assert exc_info.value.code == -32602

    def test_call_tool_type_mismatch_raises(self, tmp_path: Path) -> None:
        """get_issue 의 issue_iid 는 integer — 문자열 전달 시 에러."""
        runtime = ToolRuntime(root=tmp_path)
        with pytest.raises(McpToolError, match="기대=integer.*실제=str") as exc_info:
            call_tool(
                "get_issue",
                {"id": "my-project", "issue_iid": "not-an-int"},
                runtime,
            )
        assert exc_info.value.code == -32602

    def test_call_tool_valid_args_passes_validation(self, tmp_path: Path) -> None:
        """code_explanation 에 유효한 인자를 전달하면 validation 통과 후 handler 실행."""
        (tmp_path / "app.py").write_text("x = 1\n", encoding="utf-8")
        runtime = ToolRuntime(root=tmp_path)
        # handler 까지 정상 실행 — 예외 없음
        result = call_tool(
            "code_explanation",
            {"repo": str(tmp_path), "path": "app.py"},
            runtime,
        )
        assert "feature" in result


# ---------------------------------------------------------------------------
# JSON-RPC protocol 통합 — handle_json_rpc 에서 -32602 반환 확인
# ---------------------------------------------------------------------------


class TestJsonRpcProtocol:
    """protocol.handle_json_rpc 를 통한 end-to-end validation 에러 확인."""

    def test_json_rpc_returns_32602_on_type_error(self) -> None:
        from forgewise.protocol import handle_json_rpc

        request = {
            "jsonrpc": "2.0",
            "id": 100,
            "method": "tools/call",
            "params": {
                "name": "get_issue",
                "arguments": {"id": "proj", "issue_iid": "bad"},
            },
        }
        response = handle_json_rpc(request)
        assert response["error"]["code"] == -32602
        assert "기대=integer" in response["error"]["message"]

    def test_json_rpc_returns_32602_on_required_missing(self) -> None:
        from forgewise.protocol import handle_json_rpc

        request = {
            "jsonrpc": "2.0",
            "id": 101,
            "method": "tools/call",
            "params": {
                "name": "duo_chat",
                "arguments": {},
            },
        }
        response = handle_json_rpc(request)
        assert response["error"]["code"] == -32602
        assert "필수 인자" in response["error"]["message"]
