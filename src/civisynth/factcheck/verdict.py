"""RAG verdict pipeline: claim -> retrieve evidence -> verdict.

The deterministic rule-based judge below is used with the mock provider so
verdicts are reproducible; with a real LLM provider the judge prompt is used
instead. Labels: supported | contradicted | unverifiable.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from ..llm import LLMProvider, get_provider
from .retrieval import Evidence, EvidenceStore

LABELS = ("supported", "contradicted", "unverifiable")

_NEGATIONS = re.compile(r"\b(not|no|never|false|denied|debunked|incorrect|myth)\b", re.I)

_JUDGE_SYSTEM = (
    "You are a strict fact-check judge. Given a claim and retrieved evidence, answer "
    "with exactly one word: supported, contradicted, or unverifiable."
)


@dataclass
class Verdict:
    claim: str
    label: str
    confidence: float
    evidence: list[Evidence] = field(default_factory=list)


def _numbers(text: str) -> set[str]:
    return set(re.findall(r"\d+(?:\.\d+)?", text.replace(",", "")))


def _rule_based_judge(claim: str, evidence: list[tuple[Evidence, float]]) -> tuple[str, float]:
    if not evidence or evidence[0][1] < 0.15:
        return "unverifiable", 0.55
    top, sim = evidence[0]
    claim_nums, ev_nums = _numbers(claim), _numbers(top.text)
    claim_neg = bool(_NEGATIONS.search(claim))
    ev_neg = bool(_NEGATIONS.search(top.text))
    if claim_nums and ev_nums and claim_nums.isdisjoint(ev_nums):
        return "contradicted", min(0.9, 0.5 + sim)
    if claim_neg != ev_neg:
        return "contradicted", min(0.85, 0.45 + sim)
    return "supported", min(0.95, 0.5 + sim)


def check_claim(
    claim: str,
    store: EvidenceStore,
    llm: LLMProvider | None = None,
    k: int = 3,
) -> Verdict:
    llm = llm or get_provider()
    hits = store.search(claim, k=k)

    if llm.name == "mock":
        label, confidence = _rule_based_judge(claim, hits)
    else:
        context = "\n".join(f"[{i + 1}] {ev.text}" for i, (ev, _) in enumerate(hits))
        answer = llm.complete(
            f"Claim: {claim}\n\nEvidence:\n{context}\n\nVerdict:", system=_JUDGE_SYSTEM
        ).strip().lower()
        label = next((lab for lab in LABELS if lab in answer), "unverifiable")
        confidence = 0.8 if label != "unverifiable" else 0.5

    return Verdict(
        claim=claim, label=label, confidence=confidence, evidence=[ev for ev, _ in hits]
    )
