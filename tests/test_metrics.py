"""Prometheus 메트릭 엔드포인트 테스트."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from forgewise.http_server import HttpServerConfig, create_app
from forgewise.metrics import (
    METRICS_AVAILABLE,
    get_metrics_state,
    metrics_available,
    record_error,
    record_tool_call,
    render_metrics,
    track_duration,
)

# ---------------------------------------------------------------------------
# metrics.py 단위 테스트
# ---------------------------------------------------------------------------


def test_metrics_available_returns_true() -> None:
    """prometheus-client 가 설치된 환경에서 True 반환."""
    assert metrics_available() is True
    assert METRICS_AVAILABLE is True


def test_record_tool_call_increments_counter() -> None:
    """tool 호출 카운터가 정상 증가하는지 확인."""
    state_before = get_metrics_state()
    before_count = state_before["tool_calls"].get("test_dummy_tool", 0.0)

    record_tool_call("test_dummy_tool")

    state_after = get_metrics_state()
    after_count = state_after["tool_calls"].get("test_dummy_tool", 0.0)
    assert after_count == before_count + 1.0


def test_record_error_increments_counter() -> None:
    """에러 카운터가 정상 증가하는지 확인."""
    state_before = get_metrics_state()
    before_count = state_before["errors"].get("test_error_type", 0.0)

    record_error("test_error_type")

    state_after = get_metrics_state()
    after_count = state_after["errors"].get("test_error_type", 0.0)
    assert after_count == before_count + 1.0


def test_track_duration_context_manager() -> None:
    """track_duration 컨텍스트 매니저가 예외 없이 동작."""
    with track_duration():
        _ = 1 + 1  # 단순 연산


def test_render_metrics_returns_prometheus_format() -> None:
    """render_metrics 가 Prometheus text format 바이트와 content-type 을 반환."""
    body, content_type = render_metrics()
    assert isinstance(body, bytes)
    assert b"forgewise_" in body
    assert "text/plain" in content_type or "text/openmetrics" in content_type


def test_get_metrics_state_structure() -> None:
    """get_metrics_state 가 올바른 dict 구조를 반환."""
    state = get_metrics_state()
    assert state["available"] is True
    assert "tool_calls" in state
    assert "errors" in state


# ---------------------------------------------------------------------------
# /metrics HTTP 엔드포인트 테스트
# ---------------------------------------------------------------------------


def test_metrics_endpoint_returns_prometheus_format(tmp_path: Path) -> None:
    """/metrics 엔드포인트가 Prometheus text format 을 반환."""
    app = create_app(HttpServerConfig(repo_root=tmp_path, oauth_store_path=tmp_path / "oauth.db"))
    client = TestClient(app)

    response = client.get("/metrics")

    assert response.status_code == 200
    assert b"forgewise_" in response.content
    content_type = response.headers["content-type"]
    assert "text/plain" in content_type or "text/openmetrics" in content_type


def test_metrics_endpoint_reflects_tool_call(tmp_path: Path) -> None:
    """/metrics 가 tool 호출 후 카운터 반영을 확인."""
    app = create_app(HttpServerConfig(repo_root=tmp_path, oauth_store_path=tmp_path / "oauth.db"))
    client = TestClient(app)

    # tool 호출 실행
    client.post(
        "/api/v4/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "get_mcp_server_version"},
        },
    )

    # /metrics 에서 카운터 확인
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"forgewise_tool_calls_total" in response.content
    assert b"get_mcp_server_version" in response.content


def test_metrics_endpoint_reflects_request_duration(tmp_path: Path) -> None:
    """/metrics 가 요청 처리 시간 히스토그램을 포함."""
    app = create_app(HttpServerConfig(repo_root=tmp_path, oauth_store_path=tmp_path / "oauth.db"))
    client = TestClient(app)

    # tool 호출로 duration 기록
    client.post(
        "/api/v4/mcp",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {"name": "get_mcp_server_version"},
        },
    )

    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"forgewise_request_duration_seconds" in response.content
