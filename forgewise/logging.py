"""ForgeWise 구조화 로깅 (JSON formatter + 환경변수 제어).

Kubernetes 환경에서 JSON 형식 로그를 표준 출력으로 전송한다.
외부 의존성 없이 Python 표준 라이브러리만 사용.

환경변수:
    FORGEWISE_LOG_LEVEL: 로그 레벨 (기본: INFO).
        유효값: DEBUG, INFO, WARNING, ERROR, CRITICAL.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import UTC, datetime


class JsonFormatter(logging.Formatter):
    """logging.LogRecord를 단일 JSON 행으로 직렬화하는 포매터."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "module": record.module,
            "message": record.getMessage(),
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


def setup_logging(level: str | None = None) -> None:
    """JSON 포매터를 루트 로거에 설정한다.

    Args:
        level: 로그 레벨 문자열. ``None`` 이면 ``FORGEWISE_LOG_LEVEL``
               환경변수를 읽고, 환경변수도 없으면 ``INFO`` 를 기본값으로 사용한다.
    """
    resolved = (level if level is not None else os.getenv("FORGEWISE_LOG_LEVEL", "INFO")).upper()
    numeric_level = getattr(logging, resolved, None)
    if not isinstance(numeric_level, int):
        numeric_level = logging.INFO

    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    # 중복 핸들러 방지: 이미 JsonFormatter 핸들러가 있으면 제거 후 재설정
    root.handlers = [h for h in root.handlers if not isinstance(h.formatter, JsonFormatter)]
    root.addHandler(handler)
    root.setLevel(numeric_level)
