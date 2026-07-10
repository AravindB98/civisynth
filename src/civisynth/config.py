"""Central configuration, driven by environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    llm_provider: str = "mock"        # mock | anthropic | openai
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    anthropic_model: str = "claude-sonnet-5"
    openai_model: str = "gpt-4o-mini"
    embedding_dim: int = 256
    narrative_threshold: float = 0.35  # cosine similarity to join a narrative cluster


def load_settings() -> Settings:
    return Settings(
        llm_provider=os.getenv("CIVISYNTH_LLM_PROVIDER", "mock"),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        anthropic_model=os.getenv("CIVISYNTH_ANTHROPIC_MODEL", "claude-sonnet-5"),
        openai_model=os.getenv("CIVISYNTH_OPENAI_MODEL", "gpt-4o-mini"),
        embedding_dim=int(os.getenv("CIVISYNTH_EMBEDDING_DIM", "256")),
        narrative_threshold=float(os.getenv("CIVISYNTH_NARRATIVE_THRESHOLD", "0.35")),
    )
