"""Anthropic Claude provider (requires ANTHROPIC_API_KEY)."""

from __future__ import annotations

import httpx

from ..config import Settings

API_URL = "https://api.anthropic.com/v1/messages"


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, settings: Settings):
        if not settings.anthropic_api_key:
            raise RuntimeError(
                "ANTHROPIC_API_KEY is not set. Export it or use CIVISYNTH_LLM_PROVIDER=mock."
            )
        self._key = settings.anthropic_api_key
        self._model = settings.anthropic_model

    def complete(self, prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        payload = {
            "model": self._model,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            payload["system"] = system
        resp = httpx.post(
            API_URL,
            json=payload,
            headers={
                "x-api-key": self._key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            timeout=60,
        )
        resp.raise_for_status()
        return "".join(
            block["text"] for block in resp.json()["content"] if block["type"] == "text"
        )
