"""CiviSynth quickstart: exercises all four modules offline (mock LLM).

Run from the repo root:  python examples/quickstart.py
"""

from datetime import date, datetime, timedelta, timezone

from civisynth.factcheck import EvidenceStore, check_claim, extract_claims
from civisynth.forecast import Poll, forecast
from civisynth.ingest.models import Document
from civisynth.legislation import Bill, passage_score, summarize_bill
from civisynth.narratives import NarrativeTracker

now = datetime.now(timezone.utc)

print("=" * 60)
print("1. NARRATIVE TRACKING")
print("=" * 60)
tracker = NarrativeTracker()
articles = [
    Document(title="Senate debates sweeping tax reform bill",
             text="The senate opened debate on the tax reform bill today.",
             source="Daily Ledger", leaning="center", published=now - timedelta(hours=2)),
    Document(title="Tax reform bill faces senate showdown",
             text="Senators clashed over the proposed tax reform bill.",
             source="Morning Post", leaning="left", published=now - timedelta(hours=1)),
    Document(title="Tax bill debate heats up in the senate",
             text="Debate over the tax reform bill intensified in the senate.",
             source="National Review Daily", leaning="right", published=now),
    Document(title="Wildfire season starts early in the west",
             text="Officials warned of an early and severe wildfire season.",
             source="Daily Ledger", leaning="center", published=now),
]
tracker.add_all(articles)
for n in tracker.top(3):
    print(f"  [{n.id}] {n.label!r} size={n.size} momentum24h={n.momentum()} "
          f"spectrum={n.spectrum}")

print()
print("=" * 60)
print("2. FACT-CHECKING (RAG)")
print("=" * 60)
speech = ("The unemployment rate fell to 3.9 percent in June. "
          "Crime increased by 40 percent last year in major cities.")
store = EvidenceStore()
store.add("Bureau of Labor Statistics data shows the unemployment rate fell to 3.9 "
          "percent in June", source="BLS")
store.add("FBI statistics show violent crime in major cities increased by 12 percent "
          "last year", source="FBI")
for claim in extract_claims(speech):
    v = check_claim(claim, store)
    print(f"  [{v.label:<13}] ({v.confidence:.2f}) {v.claim}")

print()
print("=" * 60)
print("3. LEGISLATIVE INTELLIGENCE")
print("=" * 60)
bill = Bill(
    identifier="HR-2048",
    title="Rural Broadband Expansion Act",
    text="This act directs 40 billion dollars toward broadband deployment in rural "
         "areas. Grants are administered by the FCC. Providers must meet minimum "
         "speed requirements of 100 megabits per second.",
    sponsors=["Rep. A", "Rep. B", "Rep. C"],
    sponsor_parties=["D", "R"],
    stage="committee",
)
print(f"  Summary: {summarize_bill(bill)}")
print(f"  Passage probability: {passage_score(bill):.1%}")

print()
print("=" * 60)
print("4. ELECTION FORECAST")
print("=" * 60)
polls = [
    Poll("Acme Polling", date.today() - timedelta(days=3), 1200,
         {"Rivera": 48.5, "Chen": 45.0}, rating=1.2),
    Poll("StatePoll", date.today() - timedelta(days=7), 800,
         {"Rivera": 47.0, "Chen": 46.5}, rating=0.9),
    Poll("CivicSurvey", date.today() - timedelta(days=1), 1500,
         {"Rivera": 49.0, "Chen": 44.5}, rating=1.0),
]
result = forecast(polls)
print(f"  Weighted means:    {result.means}")
print(f"  Win probabilities: {result.win_probability}")
print(f"  ({result.simulations:,} simulations, sigma={result.details['sigma']})")
