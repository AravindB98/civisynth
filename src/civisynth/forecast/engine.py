"""Election forecasting: weighted poll aggregation + Monte Carlo simulation.

Every poll is weighted by recency (exponential decay), sample size (sqrt),
and pollster rating. Candidate support is the weighted mean; uncertainty
combines sampling error with systematic polling error (historically ~3 pts),
and thousands of simulated elections yield win probabilities.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from datetime import date

HALF_LIFE_DAYS = 14.0
SYSTEMATIC_ERROR = 3.0  # historical average polling miss, percentage points


@dataclass
class Poll:
    pollster: str
    end_date: date
    sample_size: int
    results: dict[str, float]          # candidate -> percent
    rating: float = 1.0                # pollster quality multiplier (0.1 - 1.5)


@dataclass
class ForecastResult:
    means: dict[str, float]
    win_probability: dict[str, float]
    simulations: int
    poll_count: int
    details: dict = field(default_factory=dict)


def _weight(poll: Poll, as_of: date) -> float:
    age = max((as_of - poll.end_date).days, 0)
    recency = 0.5 ** (age / HALF_LIFE_DAYS)
    size = math.sqrt(max(poll.sample_size, 1)) / math.sqrt(1000)
    return recency * size * poll.rating


def weighted_average(polls: list[Poll], as_of: date | None = None) -> dict[str, float]:
    as_of = as_of or max(p.end_date for p in polls)
    totals: dict[str, float] = {}
    weights: dict[str, float] = {}
    for poll in polls:
        w = _weight(poll, as_of)
        for candidate, pct in poll.results.items():
            totals[candidate] = totals.get(candidate, 0.0) + pct * w
            weights[candidate] = weights.get(candidate, 0.0) + w
    return {c: totals[c] / weights[c] for c in totals}


def forecast(
    polls: list[Poll],
    simulations: int = 10_000,
    as_of: date | None = None,
    seed: int | None = 42,
) -> ForecastResult:
    if not polls:
        raise ValueError("At least one poll is required.")
    rng = random.Random(seed)
    means = weighted_average(polls, as_of)
    candidates = list(means)

    # Sampling error from the average poll, plus systematic error.
    avg_n = sum(p.sample_size for p in polls) / len(polls)
    sampling_error = 100 * math.sqrt(0.25 / avg_n)
    sigma = math.sqrt(sampling_error**2 + SYSTEMATIC_ERROR**2)

    wins = {c: 0 for c in candidates}
    for _ in range(simulations):
        shared = rng.gauss(0, SYSTEMATIC_ERROR / 2)  # correlated national swing
        draw = {
            c: means[c] + shared * (1 if i == 0 else -1) + rng.gauss(0, sigma)
            for i, c in enumerate(candidates)
        }
        wins[max(draw, key=lambda c: draw[c])] += 1

    return ForecastResult(
        means={c: round(v, 2) for c, v in means.items()},
        win_probability={c: round(w / simulations, 4) for c, w in wins.items()},
        simulations=simulations,
        poll_count=len(polls),
        details={"sigma": round(sigma, 2), "avg_sample_size": round(avg_n)},
    )


def backtest(polls: list[Poll], actual: dict[str, float], as_of: date | None = None) -> dict:
    """Compare the weighted average against a known result."""
    predicted = weighted_average(polls, as_of)
    errors = {c: round(predicted.get(c, 0.0) - actual[c], 2) for c in actual}
    mae = sum(abs(e) for e in errors.values()) / len(errors)
    correct_winner = max(predicted, key=lambda c: predicted[c]) == max(
        actual, key=lambda c: actual[c]
    )
    return {"errors": errors, "mae": round(mae, 2), "correct_winner": correct_winner}
