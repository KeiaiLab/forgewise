"""LLM 백엔드 추상화 모듈 테스트."""

from __future__ import annotations

import json
import os
from typing import Any
from unittest import mock

import httpx

from forgewise.llm import LLMClient, LLMConfig

# --- LLMConfig 테스트 ---


def test_config_defaults() -> None:
    """기본값: backend=none, Ollama URL, llama3.2 모델."""
    config = LLMConfig()
    assert config.backend == "none"
    assert config.base_url == "http://localhost:11434"
    assert config.model == "llama3.2"
    assert config.api_key == ""
    assert config.timeout == 60.0
    assert config.max_tokens == 2048


def test_config_from_env_none_backend() -> None:
    """FORGEWISE_LLM_BACKEND 미설정 시 backend=none."""
    with mock.patch.dict(os.environ, {}, clear=True):
        config = LLMConfig.from_env()
    assert config.backend == "none"


def test_config_from_env_ollama() -> None:
    """Ollama 백엔드 환경변수 설정."""
    env = {
        "FORGEWISE_LLM_BACKEND": "ollama",
        "FORGEWISE_LLM_MODEL": "codellama",
        "FORGEWISE_LLM_TIMEOUT": "30",
        "FORGEWISE_LLM_MAX_TOKENS": "1024",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        config = LLMConfig.from_env()
    assert config.backend == "ollama"
    assert config.base_url == "http://localhost:11434"
    assert config.model == "codellama"
    assert config.timeout == 30.0
    assert config.max_tokens == 1024


def test_config_from_env_openai() -> None:
    """OpenAI 백엔드 환경변수 설정."""
    env = {
        "FORGEWISE_LLM_BACKEND": "openai",
        "FORGEWISE_LLM_API_KEY": "sk-test-key",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        config = LLMConfig.from_env()
    assert config.backend == "openai"
    assert config.base_url == "https://api.openai.com"
    assert config.model == "gpt-4o-mini"
    assert config.api_key == "sk-test-key"


def test_config_from_env_custom_base_url() -> None:
    """커스텀 base_url 이 trailing slash 제거."""
    env = {
        "FORGEWISE_LLM_BACKEND": "openai",
        "FORGEWISE_LLM_BASE_URL": "http://localhost:8000/",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        config = LLMConfig.from_env()
    assert config.base_url == "http://localhost:8000"


# --- LLMClient 테스트 ---


def test_client_not_available_when_none() -> None:
    """backend=none 이면 available=False."""
    client = LLMClient(LLMConfig(backend="none"))
    assert not client.available


def test_client_available_when_ollama() -> None:
    """backend=ollama 이면 available=True."""
    client = LLMClient(LLMConfig(backend="ollama"))
    assert client.available


def test_generate_returns_empty_when_not_available() -> None:
    """backend=none 이면 빈 문자열 반환."""
    client = LLMClient(LLMConfig(backend="none"))
    result = client.generate("hello")
    assert result == ""


def _mock_transport(response_body: dict[str, Any], status_code: int = 200) -> httpx.MockTransport:
    """테스트용 MockTransport 생성."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code, json=response_body)

    return httpx.MockTransport(handler)


def test_ollama_generate_success() -> None:
    """Ollama 정상 응답 시 response 필드 반환."""
    transport = _mock_transport({"response": "안녕하세요, 코드 설명입니다."})
    http_client = httpx.Client(transport=transport)
    client = LLMClient(
        LLMConfig(backend="ollama", base_url="http://localhost:11434"),
        http_client=http_client,
    )
    result = client.generate("explain this code", "system prompt")
    assert result == "안녕하세요, 코드 설명입니다."


def test_openai_generate_success() -> None:
    """OpenAI 정상 응답 시 choices[0].message.content 반환."""
    transport = _mock_transport(
        {
            "choices": [
                {"message": {"content": "이것은 AI 응답입니다."}}
            ]
        }
    )
    http_client = httpx.Client(transport=transport)
    client = LLMClient(
        LLMConfig(backend="openai", base_url="http://localhost:8000", api_key="test"),
        http_client=http_client,
    )
    result = client.generate("explain this code", "system prompt")
    assert result == "이것은 AI 응답입니다."


def test_ollama_http_error_returns_empty() -> None:
    """Ollama HTTP 에러 시 빈 문자열 반환."""
    transport = _mock_transport({"error": "model not found"}, status_code=404)
    http_client = httpx.Client(transport=transport)
    client = LLMClient(
        LLMConfig(backend="ollama"),
        http_client=http_client,
    )
    result = client.generate("hello")
    assert result == ""


def test_openai_http_error_returns_empty() -> None:
    """OpenAI HTTP 에러 시 빈 문자열 반환."""
    transport = _mock_transport({"error": "unauthorized"}, status_code=401)
    http_client = httpx.Client(transport=transport)
    client = LLMClient(
        LLMConfig(backend="openai", api_key="bad-key"),
        http_client=http_client,
    )
    result = client.generate("hello")
    assert result == ""


def test_ollama_json_error_returns_empty() -> None:
    """Ollama JSON 파싱 에러 시 빈 문자열 반환."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json")

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = LLMClient(
        LLMConfig(backend="ollama"),
        http_client=http_client,
    )
    result = client.generate("hello")
    assert result == ""


def test_openai_json_error_returns_empty() -> None:
    """OpenAI JSON 파싱 에러 시 빈 문자열 반환."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json")

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = LLMClient(
        LLMConfig(backend="openai", api_key="test"),
        http_client=http_client,
    )
    result = client.generate("hello")
    assert result == ""


def test_openai_missing_choices_returns_empty() -> None:
    """OpenAI 응답에 choices 키 없으면 빈 문자열 반환."""
    transport = _mock_transport({"data": "no choices"})
    http_client = httpx.Client(transport=transport)
    client = LLMClient(
        LLMConfig(backend="openai", api_key="test"),
        http_client=http_client,
    )
    result = client.generate("hello")
    assert result == ""


def test_ollama_request_body_structure() -> None:
    """Ollama 요청 body 구조 검증."""
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(200, json={"response": "ok"})

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = LLMClient(
        LLMConfig(backend="ollama", model="test-model", max_tokens=512),
        http_client=http_client,
    )
    client.generate("test prompt", "test system")

    assert len(captured) == 1
    body = json.loads(captured[0].content)
    assert body["model"] == "test-model"
    assert body["prompt"] == "test prompt"
    assert body["system"] == "test system"
    assert body["stream"] is False
    assert body["options"]["num_predict"] == 512


def test_openai_request_body_structure() -> None:
    """OpenAI 요청 body 구조 검증."""
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "ok"}}]}
        )

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = LLMClient(
        LLMConfig(
            backend="openai",
            model="gpt-4o-mini",
            api_key="sk-test",
            max_tokens=1024,
        ),
        http_client=http_client,
    )
    client.generate("test prompt", "test system")

    assert len(captured) == 1
    body = json.loads(captured[0].content)
    assert body["model"] == "gpt-4o-mini"
    assert body["max_tokens"] == 1024
    assert body["messages"][0] == {"role": "system", "content": "test system"}
    assert body["messages"][1] == {"role": "user", "content": "test prompt"}
    assert captured[0].headers["Authorization"] == "Bearer sk-test"


def test_openai_no_system_prompt() -> None:
    """system 빈 문자열이면 system message 미포함."""
    captured: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        captured.append(request)
        return httpx.Response(
            200, json={"choices": [{"message": {"content": "ok"}}]}
        )

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport)
    client = LLMClient(
        LLMConfig(backend="openai", api_key="test"),
        http_client=http_client,
    )
    client.generate("hello")

    body = json.loads(captured[0].content)
    assert len(body["messages"]) == 1
    assert body["messages"][0]["role"] == "user"
