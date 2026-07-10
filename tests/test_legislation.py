from civisynth.legislation import Bill, diff_versions, passage_score, summarize_bill


def _bill(**kwargs):
    defaults = dict(
        identifier="HR-1",
        title="Test Act",
        text="This act directs 10 billion dollars to infrastructure. "
             "Funds are administered federally. Reporting is annual.",
    )
    defaults.update(kwargs)
    return Bill(**defaults)


def test_summarize_returns_text():
    assert len(summarize_bill(_bill())) > 10


def test_diff_counts_changes():
    result = diff_versions("section 1\nsection 2", "section 1\nsection 2 amended\nsection 3")
    assert result["lines_added"] == 2
    assert result["lines_removed"] == 1
    assert "+section 3" in result["diff"]


def test_passage_score_monotonic_in_stage():
    early = passage_score(_bill(stage="introduced"))
    late = passage_score(_bill(stage="passed_both"))
    assert 0 < early < late <= 0.99


def test_bipartisan_bonus():
    partisan = passage_score(_bill(sponsors=["A"], sponsor_parties=["D"]))
    bipartisan = passage_score(_bill(sponsors=["A", "B"], sponsor_parties=["D", "R"]))
    assert bipartisan > partisan
