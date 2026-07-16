# CiviSynth

**Open political intelligence platform** — four AI-powered modules for understanding politics, built on one shared core.

[![CI](https://github.com/AravindB98/civisynth/actions/workflows/ci.yml/badge.svg)](https://github.com/AravindB98/civisynth/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](pyproject.toml)

## ⭐ Support the project

If CiviSynth is useful or interesting to you, please **star this repo** and **fork it** — stars help others discover the project, and forks are the first step to contributing. It takes two clicks and means a lot.

## What it does

| Module | Question it answers | Techniques |
|---|---|---|
| **Narratives** | Which political stories are exploding right now, and who's pushing which framing? | Embeddings, incremental clustering, momentum & spectrum analysis |
| **Fact-check** | Is this claim supported, contradicted, or unverifiable — and by what evidence? | Claim extraction, RAG retrieval, LLM judging, **eval benchmark** |
| **Legislation** | What does this bill actually do, what changed between versions, will it pass? | LLM summarization, version diffing, passage scoring |
| **Forecast** | Who wins the election, with what probability? | Weighted poll aggregation, Monte Carlo simulation, backtesting |

## Architecture

```
                    ┌──────────────────────────────┐
                    │        Ingestion layer       │
                    │   RSS / Atom feeds → Document│
                    └──────────────┬───────────────┘
                                   │
            ┌──────────────┬───────┴──────┬──────────────┐
            ▼              ▼              ▼              ▼
      ┌──────────┐   ┌──────────┐   ┌───────────┐  ┌──────────┐
      │Narratives│   │Fact-check│   │Legislation│  │ Forecast │
      │ tracker  │   │ RAG+evals│   │ summarize │  │  engine  │
      └────┬─────┘   └────┬─────┘   └─────┬─────┘  └────┬─────┘
           │              │               │             │
           └──────┬───────┴───────┬───────┴─────────────┘
                  ▼               ▼
        ┌─────────────────┐  ┌──────────────┐
        │  Shared core    │  │  FastAPI +   │
        │ LLM providers · │  │  CLI surface │
        │ embeddings      │  └──────────────┘
        └─────────────────┘
```

**Design principles**

- **Runs offline by default.** A deterministic mock LLM provider and a hashing embedder mean everything — demo, API, tests, evals — works with zero API keys. Set `CIVISYNTH_LLM_PROVIDER=anthropic` (or `openai`) plus an API key to go live.
- **Evals are first-class.** The fact-check pipeline ships with a labeled benchmark (`data/evals/`) and a harness that reports accuracy and per-label precision/recall. CI can gate on `civisynth eval --min-accuracy 0.7`.
- **Swappable infrastructure.** The vector store, embedder, and LLM provider are all small interfaces designed to be replaced with pgvector/Qdrant, neural embeddings, or any hosted model.

## Quickstart

```bash
git clone https://github.com/AravindB98/civisynth.git
cd civisynth
pip install -e ".[dev,api]"

# Run the full demo (all four modules, offline)
python examples/quickstart.py

# Run the fact-check eval benchmark
civisynth eval

# Check a single claim
civisynth factcheck "Crime rose 40 percent last year" \
  --evidence "FBI data shows crime rose 12 percent last year"

# Start the API (docs at http://localhost:8000/docs)
civisynth serve
```

## Usage examples

**Track narratives from live feeds:**

```python
from civisynth.ingest import fetch_feed
from civisynth.narratives import NarrativeTracker

tracker = NarrativeTracker()
tracker.add_all(fetch_feed("https://example.com/politics.rss", source="Example", leaning="center"))
for n in tracker.top(5):
    print(n.label, n.size, n.momentum(), n.spectrum)
```

**Fact-check a speech:**

```python
from civisynth.factcheck import EvidenceStore, check_claim, extract_claims

store = EvidenceStore()
store.add("BLS data shows unemployment fell to 3.9 percent in June", source="BLS")
for claim in extract_claims(speech_text):
    verdict = check_claim(claim, store)
    print(verdict.label, verdict.confidence, verdict.claim)
```

**Forecast an election:**

```python
from datetime import date
from civisynth.forecast import Poll, forecast

result = forecast([
    Poll("Acme", date(2026, 7, 1), 1200, {"Rivera": 48.5, "Chen": 45.0}, rating=1.2),
])
print(result.win_probability)
```

## Testing

```bash
pytest          # 24 tests, all offline
ruff check src tests
```

## Roadmap

- [ ] Neural embedding provider (sentence-transformers / hosted APIs)
- [ ] Persistent storage (SQLite → Postgres + pgvector)
- [ ] Live connectors: congress.gov, TheyWorkForYou, national election commissions
- [ ] Trained passage-probability model to replace the heuristic baseline
- [ ] Web dashboard for narrative momentum and spectrum visualization
- [ ] Larger fact-check benchmark with adversarial cases

## Contributing

Contributions are welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) for full guidelines. The short version:

1. **⭐ Star and 🍴 fork this repository** (top-right of the page) — forking creates your own copy to work in.
2. Clone your fork: `git clone https://github.com/<your-username>/civisynth.git`
3. Create a branch: `git checkout -b feat/my-improvement`
4. Install dev dependencies: `pip install -e ".[dev,api]"`
5. Make your change, and add or update tests to cover it.
6. Verify everything passes: `pytest && ruff check src tests`
7. Commit with a clear message and push to your fork.
8. Open a Pull Request against `main` describing what and why.

Good first contributions: new RSS source presets, benchmark cases in `data/evals/`, a new eval metric, or any roadmap item.

## License

MIT — see [LICENSE](LICENSE).

---

## 🧒 Explain Like I'm 5

A truth-checking machine for politics: it tracks the stories politicians and media push, fact-checks claims against real documents (and grades its own accuracy), and follows what laws are actually being written — so citizens can see evidence instead of spin.

## 🧰 Tech Stack

Python · narrative tracking · RAG fact-checking with evals · legislative data pipelines · election intelligence

## 🌍 Real-Life Applications

- Journalists fact-checking political claims with document-backed citations
- Civic groups tracking bills and voting records
- Researchers studying how political narratives spread
