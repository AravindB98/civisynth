"""OpenAI provider (requires OPENAI_API_KEY)."""

from __future__ import annotations

import httpx

from ..config import Settings

API_URL = "https://api.openai.com/v1/chat/completions"


class OpenAIProvider:
    name = "openai"

    def __init__(self, settings: Settings):
        if not settings.openai_api_key:
            raise RuntimeError(
                "OPENAI_API_KEY is not set. Export it or use CIVISYNTH_LLM_PROVIDER=mock."
            )
        self._key = settings.openai_api_key
        self._model = settings.openai_model

    def complete(self, prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = httpx.post(
            API_URL,
            json={"model": self._model, "messages": messages, "max_tokens": max_tokens},
            headers={"Authorization": f"Bearer {self._key}"},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]
