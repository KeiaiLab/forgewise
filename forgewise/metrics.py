"""Prometheus 메트릭 모듈.

prometheus-client 가 설치되지 않은 환경에서는 모든 메트릭 기록이 no-op 으로 동작한다.
"""

from __future__ import annotations

import time
from collections.abc import Generator
from contextlib import contextmanager
from typing import TYPE_CHECKING, Any

try:
    from prometheus_client import (
        CONTENT_TYPE_LATEST,
        Counter,
        Histogram,
        generate_latest,
    )

    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

if TYPE_CHECKING:
    from prometheus_client import Counter as CounterType
    from prometheus_client import Histogram as HistogramType

# ---------------------------------------------------------------------------
# 실제 Prometheus 메트릭 (설치 시에만 생성)
# ---------------------------------------------------------------------------
if METRICS_AVAILABLE:
    TOOL_CALLS: CounterType = Counter(
        "forgewise_tool_calls_total",
        "MCP tool 호출 수",
        ["tool"],
    )
    REQUEST_DURATION: HistogramType = Histogram(
        "forgewise_request_duration_seconds",
        "요청 처리 시간",
    )
    ERRORS: CounterType = Counter(
        "forgewise_errors_total",
        "에러 수",
        ["type"],
    )


# ---------------------------------------------------------------------------
# 공개 API — prometheus-client 유무에 관계없이 안전하게 호출 가능
# ---------------------------------------------------------------------------


def record_tool_call(tool_name: str) -> None:
    """tool 호출 카운터 증가."""
    if METRICS_AVAILABLE:
        TOOL_CALLS.labels(tool=tool_name).inc()


def record_error(error_type: str) -> None:
    """에러 카운터 증가."""
    if METRICS_AVAILABLE:
        ERRORS.labels(type=error_type).inc()


@contextmanager
def track_duration() -> Generator[None, None, None]:
    """요청 처리 시간 기록 컨텍스트 매니저."""
    if METRICS_AVAILABLE:
        start = time.monotonic()
        try:
            yield
        finally:
            REQUEST_DURATION.observe(time.monotonic() - start)
    else:
        yield


def render_metrics() -> tuple[bytes, str]:
    """Prometheus text format 응답 반환.

    Returns:
        (body_bytes, content_type) 튜플.

    Raises:
        RuntimeError: prometheus-client 미설치 시.
    """
    if not METRICS_AVAILABLE:
        raise RuntimeError("prometheus-client 가 설치되지 않았습니다.")
    body: bytes = generate_latest()
    content_type: str = CONTENT_TYPE_LATEST
    return body, content_type


def metrics_available() -> bool:
    """prometheus-client 설치 여부."""
    return METRICS_AVAILABLE


def get_metrics_state() -> dict[str, Any]:
    """현재 메트릭 상태 (디버깅·테스트용)."""
    if not METRICS_AVAILABLE:
        return {"available": False}
    return {
        "available": True,
        "tool_calls": {
            sample.labels["tool"]: sample.value
            for metric in TOOL_CALLS.collect()
            for sample in metric.samples
            if sample.name == "forgewise_tool_calls_total"
        },
        "errors": {
            sample.labels["type"]: sample.value
            for metric in ERRORS.collect()
            for sample in metric.samples
            if sample.name == "forgewise_errors_total"
        },
    }
