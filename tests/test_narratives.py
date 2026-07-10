from datetime import datetime, timedelta, timezone

from civisynth.ingest.models import Document
from civisynth.narratives import NarrativeTracker

NOW = datetime.now(timezone.utc)


def _doc(title, text, source="s", leaning="", hours_ago=0):
    return Document(title=title, text=text, source=source, leaning=leaning,
                    published=NOW - timedelta(hours=hours_ago))


def test_similar_articles_cluster_together():
    tracker = NarrativeTracker()
    tracker.add_all([
        _doc("Senate debates sweeping tax reform bill",
             "The senate opened debate on the tax reform bill.", "A", "left", 3),
        _doc("Tax reform bill faces senate showdown",
             "Senators clashed over the tax reform bill.", "B", "right", 2),
        _doc("Wildfire season starts early in the west",
             "Officials warned of a severe wildfire season.", "A", "center", 1),
    ])
    sizes = sorted(n.size for n in tracker.narratives)
    assert sizes == [1, 2]


def test_top_returns_labels_and_spectrum():
    tracker = NarrativeTracker()
    tracker.add(_doc("Tax reform bill debate", "Senate debates the tax bill.", "A", "left"))
    top = tracker.top(1)
    assert top[0].label
    assert top[0].spectrum["left"] == 1
    assert top[0].momentum() == 1
