"""Evaluation harness for the fact-check pipeline.

Benchmark format (JSONL), one case per line:

    {"claim": "...", "evidence": ["...", "..."], "label": "supported"}

Run:  civisynth eval  (or  python -m civisynth.factcheck.evals <path>)
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path

from ..llm import LLMProvider
from .retrieval import EvidenceStore
from .verdict import LABELS, check_claim


@dataclass
class EvalReport:
    total: int = 0
    correct: int = 0
    per_label: dict[str, dict[str, int]] = field(default_factory=dict)
    failures: list[dict] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        return self.correct / self.total if self.total else 0.0

    def summary(self) -> str:
        lines = [f"Accuracy: {self.correct}/{self.total} = {self.accuracy:.1%}"]
        for label in LABELS:
            stats = self.per_label.get(label, {})
            tp = stats.get("tp", 0)
            fp = stats.get("fp", 0)
            fn = stats.get("fn", 0)
            precision = tp / (tp + fp) if tp + fp else 0.0
            recall = tp / (tp + fn) if tp + fn else 0.0
            lines.append(f"  {label:<13} precision={precision:.2f} recall={recall:.2f}")
        return "\n".join(lines)


def load_benchmark(path: str | Path) -> list[dict]:
    cases = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if line:
            cases.append(json.loads(line))
    return cases


def run_eval(cases: list[dict], llm: LLMProvider | None = None) -> EvalReport:
    report = EvalReport(total=len(cases))
    for case in cases:
        store = EvidenceStore()
        store.add_all(case.get("evidence", []), source="benchmark")
        verdict = check_claim(case["claim"], store, llm=llm)
        expected = case["label"]
        stats_pred = report.per_label.setdefault(verdict.label, {"tp": 0, "fp": 0, "fn": 0})
        stats_true = report.per_label.setdefault(expected, {"tp": 0, "fp": 0, "fn": 0})
        if verdict.label == expected:
            report.correct += 1
            stats_pred["tp"] += 1
        else:
            stats_pred["fp"] += 1
            stats_true["fn"] += 1
            report.failures.append(
                {"claim": case["claim"], "expected": expected, "got": verdict.label}
            )
    return report


def main() -> None:
    default = Path(__file__).resolve().parents[3] / "data/evals/claims_benchmark.jsonl"
    path = sys.argv[1] if len(sys.argv) > 1 else str(default)
    report = run_eval(load_benchmark(path))
    print(report.summary())
    if report.failures:
        print("\nFailures:")
        for f in report.failures:
            print(f"  claim={f['claim']!r} expected={f['expected']} got={f['got']}")


if __name__ == "__main__":
    main()
