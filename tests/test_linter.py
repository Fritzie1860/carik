import pytest
from infrastructure.heuristic_linter import HeuristicRoboticLinter


def test_cliche_detection():
    linter = HeuristicRoboticLinter()
    sample_text = "We will delve into this rich tapestry to unlock seamless solutions. Furthermore, it is a testament."
    unique_cliches, detailed = linter.detect_cliches(sample_text)
    
    assert "delve" in unique_cliches
    assert "tapestry" in unique_cliches
    assert "unlock" in unique_cliches
    assert "testament" in unique_cliches
    assert len(detailed) >= 4


def test_em_dash_counting():
    linter = HeuristicRoboticLinter()
    assert linter.count_em_dashes("Simple sentence without dashes.") == 0
    assert linter.count_em_dashes("This is one — dash and another — dash.") == 2
    assert linter.count_em_dashes("Using standard -- double dash.") == 1


def test_burstiness_calculation():
    linter = HeuristicRoboticLinter()
    # Monotonous sentences (all 5 words)
    monotonous = ["This is a simple test.", "That is another test line.", "Here is one more test."]
    score, lengths, total = linter.calculate_burstiness(monotonous)
    assert score == 0.0

    # High burstiness sentences (mix of 3-word punchy, 25-word complex, and 4-word punchy)
    varied = [
        "Code speaks clearly.",
        "When software engineering teams build large distributed architectures across multiple cloud regions, latency, network partitions, and data replication resilience become critically important factors for uptime.",
        "Simplicity wins every time.",
        "We measure each metric meticulously to eliminate ambiguity and prevent systemic failures before they reach production environments."
    ]
    score_varied, lengths_varied, total_varied = linter.calculate_burstiness(varied)
    assert score_varied >= 8.5
