"""Claim extraction: split political text into individually checkable claims."""

from __future__ import annotations

from ..llm import LLMProvider, get_provider

_PROMPT = """[CLAIMS] {text}"""

_SYSTEM = (
    "Extract every distinct, individually verifiable factual claim from the text. "
    "Return one claim per line prefixed with '- '. Ignore opinions and rhetoric."
)


def extract_claims(text: str, llm: LLMProvider | None = None) -> list[str]:
    llm = llm or get_provider()
    raw = llm.complete(_PROMPT.format(text=text), system=_SYSTEM)
    claims = []
    for line in raw.splitlines():
        line = line.strip().lstrip("-•* ").strip()
        if line:
            claims.append(line)
    return claims
