# Contributing to CiviSynth

Thanks for your interest in contributing! This document explains the process end to end.

## Step 0: Star and fork

Before anything else, please **star ⭐ the repository** (it helps the project's visibility) and **fork 🍴 it** to your own account — all contributions flow through pull requests from forks.

## Ways to contribute

- **Code**: new features, bug fixes, performance improvements
- **Benchmark data**: add labeled cases to `data/evals/claims_benchmark.jsonl` — more diverse, harder cases make the eval more meaningful
- **Connectors**: RSS presets, legislature scrapers, poll data importers
- **Docs**: clarify the README, add usage examples, fix typos
- **Issues**: well-written bug reports and feature requests are contributions too

## Development setup

```bash
git clone https://github.com/<your-username>/civisynth.git
cd civisynth
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev,api]"
pytest   # should pass out of the box, fully offline
```

## Workflow

1. Open or find an issue describing the change (for anything non-trivial).
2. Create a feature branch: `git checkout -b feat/short-description`.
3. Write the code **and tests** — PRs without tests for new behavior won't be merged.
4. Keep the offline guarantee: everything must work with the mock LLM provider and no network. Network-dependent code paths need a mockable interface.
5. Run the checks: `pytest && ruff check src tests`.
6. Commit with clear messages (imperative mood: "Add pollster rating decay").
7. Push and open a PR against `main`. Fill in what changed, why, and how you tested it.

## Code standards

- Python 3.10+, type hints on public functions
- Ruff for linting (line length 100)
- Small, focused modules — follow the existing structure
- No new required dependencies without discussion; optional extras are fine

## Adding benchmark cases

Each line in `data/evals/claims_benchmark.jsonl` is:

```json
{"claim": "...", "evidence": ["...", "..."], "label": "supported|contradicted|unverifiable"}
```

Guidelines: claims should be atomic and checkable; evidence should be realistic; include hard negatives (evidence that is topically similar but doesn't settle the claim).

## Reporting security issues

Please do not open public issues for security problems — email the maintainer instead.

## Code of conduct

Be respectful and constructive. Political topics attract strong opinions; keep discussion technical and evidence-based. Harassment or bad-faith participation results in a ban.
