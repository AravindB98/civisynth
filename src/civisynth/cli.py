"""CiviSynth command line interface."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date


def _cmd_eval(args: argparse.Namespace) -> int:
    from .factcheck.evals import load_benchmark, run_eval

    report = run_eval(load_benchmark(args.benchmark))
    print(report.summary())
    return 0 if report.accuracy >= args.min_accuracy else 1


def _cmd_factcheck(args: argparse.Namespace) -> int:
    from .factcheck import EvidenceStore, check_claim

    store = EvidenceStore()
    for ev in args.evidence or []:
        store.add(ev, source="cli")
    verdict = check_claim(args.claim, store)
    print(json.dumps({"claim": verdict.claim, "label": verdict.label,
                      "confidence": verdict.confidence}, indent=2))
    return 0


def _cmd_forecast(args: argparse.Namespace) -> int:
    from .forecast import Poll, forecast

    raw = json.load(open(args.polls))
    polls = [
        Poll(
            pollster=p["pollster"],
            end_date=date.fromisoformat(p["end_date"]),
            sample_size=p["sample_size"],
            results=p["results"],
            rating=p.get("rating", 1.0),
        )
        for p in raw
    ]
    result = forecast(polls)
    print(json.dumps({"means": result.means, "win_probability": result.win_probability},
                     indent=2))
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    from .api import create_app

    uvicorn.run(create_app(), host=args.host, port=args.port)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="civisynth",
                                     description="Open political intelligence platform")
    sub = parser.add_subparsers(dest="command", required=True)

    p_eval = sub.add_parser("eval", help="Run the fact-check eval benchmark")
    p_eval.add_argument("--benchmark", default="data/evals/claims_benchmark.jsonl")
    p_eval.add_argument("--min-accuracy", type=float, default=0.0)
    p_eval.set_defaults(func=_cmd_eval)

    p_fc = sub.add_parser("factcheck", help="Check a single claim")
    p_fc.add_argument("claim")
    p_fc.add_argument("--evidence", action="append", help="Evidence snippet (repeatable)")
    p_fc.set_defaults(func=_cmd_factcheck)

    p_fx = sub.add_parser("forecast", help="Forecast from a polls JSON file")
    p_fx.add_argument("polls", help="Path to polls JSON")
    p_fx.set_defaults(func=_cmd_forecast)

    p_serve = sub.add_parser("serve", help="Start the API server")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.set_defaults(func=_cmd_serve)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
