"""Narrative tracking: incremental clustering of political coverage.

Each incoming document is embedded and assigned to the closest existing
narrative cluster (centroid cosine similarity above a threshold) or starts a
new one. Clusters accumulate a timeline, per-source counts, and a
left/center/right spectrum split, which yields momentum and framing-spread
metrics — the core of "what's exploding right now and who's pushing it".
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from ..config import Settings, load_settings
from ..embeddings import Embedder, HashingEmbedder, cosine
from ..ingest.models import Document
from ..llm import LLMProvider, get_provider


@dataclass
class Narrative:
    id: int
    centroid: list[float]
    documents: list[Document] = field(default_factory=list)
    label: str = ""

    @property
    def size(self) -> int:
        return len(self.documents)

    @property
    def sources(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for d in self.documents:
            counts[d.source] = counts.get(d.source, 0) + 1
        return counts

    @property
    def spectrum(self) -> dict[str, int]:
        counts = {"left": 0, "center": 0, "right": 0, "unknown": 0}
        for d in self.documents:
            counts[d.leaning if d.leaning in counts else "unknown"] += 1
        return counts

    def momentum(self, window: timedelta = timedelta(hours=24)) -> int:
        """Documents added within the trailing window."""
        cutoff = datetime.now(timezone.utc) - window
        return sum(1 for d in self.documents if d.published >= cutoff)


class NarrativeTracker:
    def __init__(
        self,
        embedder: Embedder | None = None,
        llm: LLMProvider | None = None,
        settings: Settings | None = None,
    ):
        self.settings = settings or load_settings()
        self.embedder = embedder or HashingEmbedder(self.settings.embedding_dim)
        self.llm = llm or get_provider(self.settings)
        self.narratives: list[Narrative] = []
        self._next_id = 1

    def add(self, doc: Document) -> Narrative:
        vec = self.embedder.embed(doc.full_text)
        best, best_sim = None, -1.0
        for narrative in self.narratives:
            sim = cosine(vec, narrative.centroid)
            if sim > best_sim:
                best, best_sim = narrative, sim

        if best is not None and best_sim >= self.settings.narrative_threshold:
            n = best.size
            best.centroid = [
                (c * n + v) / (n + 1) for c, v in zip(best.centroid, vec)
            ]
            best.documents.append(doc)
            return best

        narrative = Narrative(id=self._next_id, centroid=vec, documents=[doc])
        self._next_id += 1
        self.narratives.append(narrative)
        return narrative

    def add_all(self, docs: list[Document]) -> None:
        for doc in sorted(docs, key=lambda d: d.published):
            self.add(doc)

    def top(self, n: int = 10, window: timedelta = timedelta(hours=24)) -> list[Narrative]:
        """Narratives ranked by recent momentum, then total size."""
        ranked = sorted(
            self.narratives, key=lambda x: (x.momentum(window), x.size), reverse=True
        )
        top = ranked[:n]
        for narrative in top:
            if not narrative.label:
                sample = " ".join(d.title for d in narrative.documents[:5])
                narrative.label = self.llm.complete(f"[LABEL] {sample}").strip()
        return top
