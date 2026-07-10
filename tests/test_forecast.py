from datetime import date, timedelta

import pytest

from civisynth.forecast import Poll, forecast, weighted_average
from civisynth.forecast.engine import backtest

TODAY = date(2026, 7, 1)


def _polls():
    return [
        Poll("A", TODAY - timedelta(days=2), 1200, {"X": 52.0, "Y": 44.0}, rating=1.2),
        Poll("B", TODAY - timedelta(days=10), 800, {"X": 50.0, "Y": 46.0}, rating=0.9),
        Poll("C", TODAY, 1500, {"X": 53.0, "Y": 43.0}, rating=1.0),
    ]


def test_weighted_average_between_extremes():
    means = weighted_average(_polls(), as_of=TODAY)
    assert 50.0 <= means["X"] <= 53.0
    assert 43.0 <= means["Y"] <= 46.0


def test_recent_polls_weigh_more():
    old = Poll("Old", TODAY - timedelta(days=60), 1000, {"X": 30.0, "Y": 70.0})
    new = Poll("New", TODAY, 1000, {"X": 60.0, "Y": 40.0})
    means = weighted_average([old, new], as_of=TODAY)
    assert means["X"] > 55.0


def test_forecast_probabilities_sum_to_one_and_favor_leader():
    result = forecast(_polls(), simulations=5000, as_of=TODAY, seed=7)
    assert abs(sum(result.win_probability.values()) - 1.0) < 1e-9
    assert result.win_probability["X"] > result.win_probability["Y"]


def test_forecast_requires_polls():
    with pytest.raises(ValueError):
        forecast([])


def test_backtest_reports_winner_and_mae():
    report = backtest(_polls(), {"X": 51.0, "Y": 45.0}, as_of=TODAY)
    assert report["correct_winner"] is True
    assert report["mae"] < 5.0
