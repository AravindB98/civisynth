"""Minimal RSS/Atom ingestion using only the standard library + httpx."""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

import httpx

from .models import Document

_ATOM = "{http://www.w3.org/2005/Atom}"


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text or "").strip()


def _parse_date(value: str | None) -> datetime:
    if value:
        try:
            return parsedate_to_datetime(value)
        except (TypeError, ValueError):
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                pass
    return datetime.now(timezone.utc)


def parse_rss(xml_text: str, source: str = "", leaning: str = "") -> list[Document]:
    """Parse an RSS 2.0 or Atom feed string into Documents."""
    root = ET.fromstring(xml_text)
    docs: list[Document] = []

    for item in root.iter("item"):  # RSS 2.0
        title = (item.findtext("title") or "").strip()
        desc = _strip_html(item.findtext("description") or "")
        docs.append(
            Document(
                title=title,
                text=desc,
                source=source,
                url=(item.findtext("link") or "").strip(),
                published=_parse_date(item.findtext("pubDate")),
                leaning=leaning,
            )
        )

    for entry in root.iter(f"{_ATOM}entry"):  # Atom
        title = (entry.findtext(f"{_ATOM}title") or "").strip()
        summary = _strip_html(entry.findtext(f"{_ATOM}summary") or "")
        link_el = entry.find(f"{_ATOM}link")
        docs.append(
            Document(
                title=title,
                text=summary,
                source=source,
                url=link_el.get("href", "") if link_el is not None else "",
                published=_parse_date(entry.findtext(f"{_ATOM}updated")),
                leaning=leaning,
            )
        )
    return docs


def fetch_feed(url: str, source: str = "", leaning: str = "") -> list[Document]:
    """Fetch and parse a live feed."""
    resp = httpx.get(url, timeout=30, follow_redirects=True)
    resp.raise_for_status()
    return parse_rss(resp.text, source=source or url, leaning=leaning)
