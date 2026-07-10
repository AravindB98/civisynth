"""Deterministic mock LLM.

Not a language model: a set of cheap heuristics that produce sensible,
reproducible output for each prompt "task tag" so the platform, demos, and
tests all run with zero API keys or network access. Prompts built by
CiviSynth modules start with a task tag like [SUMMARIZE] or [LABEL].
"""

from __future__ import annotations

import re


def _sentences(text: str) -> list[str]:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def _top_keywords(text: str, n: int = 5) -> list[str]:
    stop = {
        "the", "a", "an", "of", "to", "and", "in", "on", "for", "is", "are", "was",
        "were", "that", "this", "it", "as", "by", "with", "be", "has", "have", "had",
        "at", "from", "will", "would", "its", "their", "they", "he", "she", "we",
    }
    words = re.findall(r"[a-zA-Z][a-zA-Z'-]+", text.lower())
    freq: dict[str, int] = {}
    for w in words:
        if w not in stop and len(w) > 2:
            freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda kv: (-kv[1], kv[0]))[:n]]


class MockProvider:
    name = "mock"

    def complete(self, prompt: str, system: str = "", max_tokens: int = 1024) -> str:
        body = prompt.split("]", 1)[-1].strip() if prompt.startswith("[") else prompt
        if prompt.startswith("[SUMMARIZE]"):
            sents = _sentences(body)
            return " ".join(sents[:3]) if sents else body[:300]
        if prompt.startswith("[LABEL]"):
            kws = _top_keywords(body, 4)
            return " / ".join(kws).title() if kws else "General Politics"
        if prompt.startswith("[CLAIMS]"):
            sents = _sentences(body)
            factual = [
                s for s in sents
                if re.search(r"\d", s)
                or re.search(r"\b(is|are|was|were|has|have|will|increased|decreased|voted)\b", s)
            ]
            return "\n".join(f"- {s}" for s in factual[:8])
        # Default: echo a trimmed body so behavior is predictable.
        return body[:max_tokens]
