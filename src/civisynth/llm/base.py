"""Pluggable LLM provider interface.

Every LLM-powered feature in CiviSynth goes through this interface, so the
whole platform runs offline with the deterministic mock provider (default)
and upgrades to Anthropic or OpenAI by setting two environment variables:

    CIVISYNTH_LLM_PROVIDER=anthropic
    ANTHROPIC_API_KEY=sk-ant-...
"""

from __future__ import annotations

from typing import Protocol

from ..config import Settings, load_settings


class LLMProvider(Protocol):
    name: str

    def complete(self, prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        """Return a completion for the prompt."""
        ...


def get_provider(settings: Settings | None = None) -> LLMProvider:
    settings = settings or load_settings()
    provider = settings.llm_provider.lower()
    if provider == "mock":
        from .mock import MockProvider

        return MockProvider()
    if provider == "anthropic":
        from .anthropic_provider import AnthropicProvider

        return AnthropicProvider(settings)
    if provider == "openai":
        from .openai_provider import OpenAIProvider

        return OpenAIProvider(settings)
    raise ValueError(f"Unknown LLM provider: {settings.llm_provider!r}")
