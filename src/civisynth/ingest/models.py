"""Shared document model used by every module."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class Document:
    title: str
    text: str
    source: str = ""
    url: str = ""
    published: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    leaning: str = ""  # optional editorial leaning of the source: left | center | right
    id: str = ""

    def __post_init__(self):
        if not self.id:
            raw = f"{self.source}|{self.title}|{self.url}"
            self.id = hashlib.sha1(raw.encode()).hexdigest()[:12]

    @property
    def full_text(self) -> str:
        return f"{self.title}. {self.text}"
