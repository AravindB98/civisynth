"""In-memory vector store for evidence retrieval.

Deliberately simple: the interface (add / search) mirrors what you would use
with a hosted vector DB, so swapping in pgvector/Qdrant/Chroma is a one-file
change.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..embeddings import Embedder, HashingEmbedder, cosine


@dataclass
class Evidence:
    text: str
    source: str = ""
    url: str = ""
    vector: list[float] = field(default_factory=list, repr=False)


class EvidenceStore:
    def __init__(self, embedder: Embedder | None = None):
        self.embedder = embedder or HashingEmbedder()
        self._items: list[Evidence] = []

    def add(self, text: str, source: str = "", url: str = "") -> Evidence:
        ev = Evidence(text=text, source=source, url=url, vector=self.embedder.embed(text))
        self._items.append(ev)
        return ev

    def add_all(self, texts: list[str], source: str = "") -> None:
        for t in texts:
            self.add(t, source=source)

    def search(self, query: str, k: int = 3) -> list[tuple[Evidence, float]]:
        qv = self.embedder.embed(query)
        scored = [(ev, cosine(qv, ev.vector)) for ev in self._items]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return scored[:k]

    def __len__(self) -> int:
        return len(self._items)
