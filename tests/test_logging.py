"""forgewise.logging 모듈 단위 테스트."""

from __future__ import annotations

import json
import logging
import os
from unittest.mock import patch

import pytest

from forgewise.logging import JsonFormatter, setup_logging


class TestJsonFormatter:
    """JsonFormatter 출력 형식 검증."""

    def setup_method(self) -> None:
        self.formatter = JsonFormatter()

    def test_기본_필드_포함(self) -> None:
        record = logging.LogRecord(
            name="forgewise.test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="테스트 메시지",
            args=None,
            exc_info=None,
        )
        output = self.formatter.format(record)
        parsed = json.loads(output)

        assert parsed["level"] == "INFO"
        assert parsed["message"] == "테스트 메시지"
        assert parsed["logger"] == "forgewise.test"
        assert parsed["module"] == "test"
        assert "timestamp" in parsed

    def test_한국어_메시지_정상_직렬화(self) -> None:
        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="app.py",
            lineno=10,
            msg="경고: 설정 파일 누락",
            args=None,
            exc_info=None,
        )
        output = self.formatter.format(record)

        # ensure_ascii=False 이므로 유니코드 이스케이프 없이 한국어 그대로 출력
        assert "경고: 설정 파일 누락" in output
        parsed = json.loads(output)
        assert parsed["message"] == "경고: 설정 파일 누락"

    def test_예외_정보_포함(self) -> None:
        try:
            raise ValueError("테스트 오류")
        except ValueError:
            import sys

            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="오류 발생",
            args=None,
            exc_info=exc_info,
        )
        output = self.formatter.format(record)
        parsed = json.loads(output)

        assert "exception" in parsed
        assert "ValueError" in parsed["exception"]
        assert "테스트 오류" in parsed["exception"]

    def test_예외_없을_때_exception_키_미포함(self) -> None:
        record = logging.LogRecord(
            name="test",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=1,
            msg="디버그",
            args=None,
            exc_info=None,
        )
        output = self.formatter.format(record)
        parsed = json.loads(output)

        assert "exception" not in parsed

    def test_포맷_인자_치환(self) -> None:
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="요청 처리: %s → %d",
            args=("/healthz", 200),
            exc_info=None,
        )
        output = self.formatter.format(record)
        parsed = json.loads(output)

        assert parsed["message"] == "요청 처리: /healthz → 200"

    def test_timestamp_ISO_형식(self) -> None:
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="ts 검증",
            args=None,
            exc_info=None,
        )
        output = self.formatter.format(record)
        parsed = json.loads(output)

        # ISO 8601 형식 + UTC 표시 확인
        ts = parsed["timestamp"]
        assert "T" in ts
        assert ts.endswith("+00:00")

    def test_출력은_유효한_단일행_JSON(self) -> None:
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="단일 행 검증",
            args=None,
            exc_info=None,
        )
        output = self.formatter.format(record)

        assert "\n" not in output
        json.loads(output)  # 유효한 JSON 이면 예외 없음


class TestSetupLogging:
    """setup_logging() 동작 검증."""

    def teardown_method(self) -> None:
        # 테스트 간 루트 로거 핸들러 정리
        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel(logging.WARNING)

    def test_기본_레벨_INFO(self) -> None:
        setup_logging()
        root = logging.getLogger()

        assert root.level == logging.INFO
        assert any(isinstance(h.formatter, JsonFormatter) for h in root.handlers)

    def test_환경변수_FORGEWISE_LOG_LEVEL_적용(self) -> None:
        with patch.dict(os.environ, {"FORGEWISE_LOG_LEVEL": "DEBUG"}):
            setup_logging()

        assert logging.getLogger().level == logging.DEBUG

    def test_명시적_레벨_인자가_환경변수보다_우선(self) -> None:
        with patch.dict(os.environ, {"FORGEWISE_LOG_LEVEL": "DEBUG"}):
            setup_logging(level="ERROR")

        assert logging.getLogger().level == logging.ERROR

    def test_잘못된_레벨은_INFO_폴백(self) -> None:
        setup_logging(level="INVALID_LEVEL")

        assert logging.getLogger().level == logging.INFO

    def test_중복_호출_시_핸들러_중복_없음(self) -> None:
        setup_logging()
        setup_logging()

        json_handlers = [
            h
            for h in logging.getLogger().handlers
            if isinstance(h.formatter, JsonFormatter)
        ]
        assert len(json_handlers) == 1

    def test_대소문자_무관(self) -> None:
        setup_logging(level="warning")

        assert logging.getLogger().level == logging.WARNING


class TestSetupLoggingIntegration:
    """setup_logging 후 실제 로거 사용 통합 검증."""

    def teardown_method(self) -> None:
        root = logging.getLogger()
        root.handlers.clear()
        root.setLevel(logging.WARNING)

    def test_로거_출력이_JSON_형식(self, capsys: pytest.CaptureFixture[str]) -> None:
        setup_logging(level="DEBUG")
        test_logger = logging.getLogger("forgewise.integration_test")
        test_logger.info("통합 테스트 메시지")

        captured = capsys.readouterr()
        parsed = json.loads(captured.err.strip())

        assert parsed["message"] == "통합 테스트 메시지"
        assert parsed["level"] == "INFO"
        assert parsed["logger"] == "forgewise.integration_test"
