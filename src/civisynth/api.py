"""FastAPI surface for all four modules.

Run:  pip install "civisynth[api]" && civisynth serve
Docs: http://localhost:8000/docs
"""

from __future__ import annotations

from datetime import date

from .factcheck import EvidenceStore, check_claim, extract_claims
from .forecast import Poll, forecast
from .legislation import Bill, diff_versions, passage_score, summarize_bill
from .narratives import NarrativeTracker


def create_app():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install API extras: pip install 'civisynth[api]'") from exc

    app = FastAPI(
        title="CiviSynth",
        description="Open political intelligence platform",
        version="0.1.0",
    )
    tracker = NarrativeTracker()

    class DocumentIn(BaseModel):
        title: str
        text: str = ""
        source: str = ""
        url: str = ""
        leaning: str = ""

    class FactCheckIn(BaseModel):
        text: str
        evidence: list[str] = []

    class BillIn(BaseModel):
        identifier: str
        title: str
        text: str
        sponsors: list[str] = []
        sponsor_parties: list[str] = []
        stage: str = "introduced"

    class DiffIn(BaseModel):
        old_text: str
        new_text: str

    class PollIn(BaseModel):
        pollster: str
        end_date: date
        sample_size: int
        results: dict[str, float]
        rating: float = 1.0

    class ForecastIn(BaseModel):
        polls: list[PollIn]
        simulations: int = 10_000

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/narratives/ingest")
    def ingest(docs: list[DocumentIn]):
        from .ingest.models import Document

        for d in docs:
            tracker.add(Document(**d.model_dump()))
        return {"narratives": len(tracker.narratives)}

    @app.get("/narratives/top")
    def top_narratives(n: int = 10):
        return [
            {
                "id": x.id,
                "label": x.label,
                "size": x.size,
                "momentum_24h": x.momentum(),
                "sources": x.sources,
                "spectrum": x.spectrum,
            }
            for x in tracker.top(n)
        ]

    @app.post("/factcheck")
    def factcheck(payload: FactCheckIn):
        store = EvidenceStore()
        store.add_all(payload.evidence, source="user")
        claims = extract_claims(payload.text)
        verdicts = [check_claim(c, store) for c in claims]
        return [
            {
                "claim": v.claim,
                "label": v.label,
                "confidence": v.confidence,
                "evidence": [e.text for e in v.evidence],
            }
            for v in verdicts
        ]

    @app.post("/legislation/summarize")
    def legislation(payload: BillIn):
        bill = Bill(**payload.model_dump())
        return {
            "identifier": bill.identifier,
            "summary": summarize_bill(bill),
            "passage_probability": passage_score(bill),
        }

    @app.post("/legislation/diff")
    def legislation_diff(payload: DiffIn):
        return diff_versions(payload.old_text, payload.new_text)

    @app.post("/forecast")
    def run_forecast(payload: ForecastIn):
        polls = [Poll(**p.model_dump()) for p in payload.polls]
        result = forecast(polls, simulations=payload.simulations)
        return {
            "means": result.means,
            "win_probability": result.win_probability,
            "simulations": result.simulations,
            "details": result.details,
        }

    return app
