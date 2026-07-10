"""Legislative intelligence: summarize bills, diff versions, score passage odds."""

from __future__ import annotations

import difflib
from dataclasses import dataclass, field

from ..llm import LLMProvider, get_provider

_SUMMARY_SYSTEM = (
    "You are a legislative analyst. Summarize the bill in plain English for a "
    "general audience: what it does, who it affects, and any notable provisions."
)

# Stage weights approximate how far through the funnel a bill has survived.
_STAGE_WEIGHTS = {
    "introduced": 0.05,
    "committee": 0.15,
    "reported": 0.35,
    "floor": 0.55,
    "passed_one_chamber": 0.75,
    "passed_both": 0.95,
    "enacted": 1.0,
}


@dataclass
class Bill:
    identifier: str            # e.g. "HR-1234"
    title: str
    text: str
    sponsors: list[str] = field(default_factory=list)
    sponsor_parties: list[str] = field(default_factory=list)
    stage: str = "introduced"
    chamber: str = ""


def summarize_bill(bill: Bill, llm: LLMProvider | None = None) -> str:
    llm = llm or get_provider()
    return llm.complete(
        f"[SUMMARIZE] {bill.identifier}: {bill.title}. {bill.text}",
        system=_SUMMARY_SYSTEM,
    ).strip()


def diff_versions(old_text: str, new_text: str) -> dict:
    """Unified diff plus a count of added/removed lines between bill versions."""
    old_lines = old_text.splitlines()
    new_lines = new_text.splitlines()
    diff = list(
        difflib.unified_diff(old_lines, new_lines, fromfile="previous", tofile="current", lineterm="")
    )
    added = sum(1 for line in diff if line.startswith("+") and not line.startswith("+++"))
    removed = sum(1 for line in diff if line.startswith("-") and not line.startswith("---"))
    return {"diff": "\n".join(diff), "lines_added": added, "lines_removed": removed}


def passage_score(bill: Bill) -> float:
    """Heuristic probability (0-1) the bill becomes law.

    Transparent baseline model: stage survival x sponsorship strength x
    bipartisanship bonus. Intended as the feature scaffold for a trained
    model (see roadmap in README).
    """
    base = _STAGE_WEIGHTS.get(bill.stage, 0.05)
    sponsor_boost = min(len(bill.sponsors), 40) / 40 * 0.15
    parties = {p.lower() for p in bill.sponsor_parties if p}
    bipartisan_bonus = 0.10 if len(parties) > 1 else 0.0
    return round(min(base + sponsor_boost + bipartisan_bonus, 0.99), 3)
