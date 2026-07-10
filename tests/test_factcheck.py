from pathlib import Path

from civisynth.factcheck import EvidenceStore, check_claim, extract_claims
from civisynth.factcheck.evals import load_benchmark, run_eval

BENCHMARK = Path(__file__).parent.parent / "data/evals/claims_benchmark.jsonl"


def test_extract_claims_finds_factual_sentences():
    text = ("The unemployment rate fell to 3.9 percent in June. "
            "What a wonderful day! "
            "The senator voted for the bill.")
    claims = extract_claims(text)
    assert any("3.9" in c for c in claims)
    assert any("voted" in c for c in claims)


def test_supported_claim():
    store = EvidenceStore()
    store.add("Official data shows the unemployment rate fell to 3.9 percent in June")
    v = check_claim("The unemployment rate fell to 3.9 percent in June", store)
    assert v.label == "supported"


def test_contradicted_claim_on_number_mismatch():
    store = EvidenceStore()
    store.add("FBI statistics show violent crime in major cities increased by 12 "
              "percent last year")
    v = check_claim("Crime increased by 40 percent last year in major cities", store)
    assert v.label == "contradicted"


def test_unverifiable_without_relevant_evidence():
    store = EvidenceStore()
    store.add("Completely unrelated gardening tips for spring vegetables")
    v = check_claim("The governor secretly met with lobbyists", store)
    assert v.label == "unverifiable"


def test_benchmark_accuracy_floor():
    report = run_eval(load_benchmark(BENCHMARK))
    assert report.total >= 10
    assert report.accuracy >= 0.7, report.summary()
