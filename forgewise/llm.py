"""LLM 백엔드 추상화 — Ollama + OpenAI-compatible 이중 지원."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class LLMConfig:
    """LLM 백엔드 설정. 환경변수 또는 직접 생성으로 초기화."""

    backend: str = "none"  # "ollama" | "openai" | "none"
    base_url: str = "http://localhost:11434"
    model: str = "llama3.2"
    api_key: str = ""
    timeout: float = 60.0
    max_tokens: int = 2048

    @classmethod
    def from_env(cls) -> LLMConfig:
        """환경변수에서 LLM 설정을 로드한다."""
        backend = os.environ.get("FORGEWISE_LLM_BACKEND", "none")
        if backend == "none":
            return cls()
        base_url = os.environ.get("FORGEWISE_LLM_BASE_URL", "")
        if not base_url:
            base_url = (
                "http://localhost:11434" if backend == "ollama" else "https://api.openai.com"
            )
        return cls(
            backend=backend,
            base_url=base_url.rstrip("/"),
            model=os.environ.get(
                "FORGEWISE_LLM_MODEL",
                "llama3.2" if backend == "ollama" else "gpt-4o-mini",
            ),
            api_key=os.environ.get("FORGEWISE_LLM_API_KEY", ""),
            timeout=float(os.environ.get("FORGEWISE_LLM_TIMEOUT", "60")),
            max_tokens=int(os.environ.get("FORGEWISE_LLM_MAX_TOKENS", "2048")),
        )


class LLMClient:
    """Ollama / OpenAI 호환 LLM 클라이언트. 미설정 시 빈 문자열 반환."""

    def __init__(
        self,
        config: LLMConfig | None = None,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.config = config or LLMConfig.from_env()
        self._http = http_client

    @property
    def available(self) -> bool:
        """LLM 백엔드가 설정되어 사용 가능한지 반환."""
        return self.config.backend != "none"

    def generate(self, prompt: str, system: str = "") -> str:
        """프롬프트에 대한 LLM 응답 반환. 미설정 시 빈 문자열."""
        if not self.available:
            return ""
        if self.config.backend == "ollama":
            return self._ollama_generate(prompt, system)
        return self._openai_generate(prompt, system)

    def _get_http(self) -> httpx.Client:
        if self._http is not None:
            return self._http
        return httpx.Client(timeout=self.config.timeout)

    def _ollama_generate(self, prompt: str, system: str) -> str:
        http = self._get_http()
        try:
            response = http.post(
                f"{self.config.base_url}/api/generate",
                json={
                    "model": self.config.model,
                    "prompt": prompt,
                    "system": system,
                    "stream": False,
                    "options": {"num_predict": self.config.max_tokens},
                },
            )
            response.raise_for_status()
            return response.json().get("response", "")
        except (httpx.HTTPError, KeyError, json.JSONDecodeError):
            return ""
        finally:
            if self._http is None:
                http.close()

    def _openai_generate(self, prompt: str, system: str) -> str:
        http = self._get_http()
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        try:
            response = http.post(
                f"{self.config.base_url}/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.config.api_key}"},
                json={
                    "model": self.config.model,
                    "messages": messages,
                    "max_tokens": self.config.max_tokens,
                },
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
            return str(data["choices"][0]["message"]["content"])
        except (httpx.HTTPError, KeyError, IndexError, json.JSONDecodeError):
            return ""
        finally:
            if self._http is None:
                http.close()
