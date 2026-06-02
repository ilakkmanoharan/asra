from __future__ import annotations

import json
from pathlib import Path

import pytest

from asra.causality.change_analyzer import ChangeAnalyzer
from asra.causality.counterfactual import CounterfactualSimulator
from asra.causality.effect_summarizer import ActionEffectSummarizer
from asra.causality.hypothesis_tester import HypothesisTester
from asra.causality.semantics_store import SemanticsStore
from asra.causality.transition_model import CausalTransitionModel
from asra.causality.uncertainty import UncertaintyScorer


def _transition(changed: int, action: str = "ACTION1", game: str = "mock", sh: str = "s1", nsh: str = "s2"):
    return {
        "game_id": game,
        "state": {"state_hash": sh, "grid": [[0, 1], [2, 3]]},
        "next_state": {"state_hash": nsh, "grid": [[0, 1], [2, 3]]},
        "action": {"name": action},
        "diff": {"num_changed_cells": changed, "delta_num_objects": 0},
        "terminal_state": False,
        "metadata": {},
    }


def test_effect_summarizer_consistency():
    s = ActionEffectSummarizer()
    for _ in range(3):
        s.observe("g1", "h1", "ACTION1", changed_cells=2, transform_histogram={"translate": 1})
    sig = s.summarize("g1", "h1", "ACTION1")
    assert sig.observation_count == 3
    assert sig.cell_change_mean == 2.0
    assert sig.confidence > 0.5
    assert sig.semantic_label in {"localized_transform", "translate", "multi_cell_transform"}


def test_transition_model_predicts():
    m = CausalTransitionModel()
    m.observe("g1", "h1", "ACTION1", "h2", changed_cells=4.0)
    m.observe("g1", "h1", "ACTION1", "h2", changed_cells=6.0)
    pred = m.predict("g1", "h1", "ACTION1")
    assert pred.predicted_next_hash == "h2"
    assert pred.support_count == 2
    assert pred.predicted_changed_cells == 5.0


def test_uncertainty_decreases_with_observations():
    scorer = UncertaintyScorer()
    from asra.causality.schemas import ActionEffectSignature

    low = scorer.score(ActionEffectSignature("A", "g", "h", observation_count=10))
    high = scorer.score(ActionEffectSignature("A", "g", "h", observation_count=0))
    assert low < high


def test_hypothesis_tester_confirms():
    tester = HypothesisTester(min_support=2)
    from asra.causality.schemas import ActionEffectSignature

    sig = ActionEffectSignature("ACTION1", "g1", "h1", observation_count=2, semantic_label="translate")
    hyp = tester.upsert_from_signature(sig)
    assert hyp.status in {"weak", "confirmed", "active"}
    updated = tester.test_observation("g1", "ACTION1", "translate", changed_cells=2, expected_cells=2)
    assert updated is not None
    assert updated.support >= 2


def test_counterfactual_lookup():
    model = CausalTransitionModel()
    model.observe("g1", "h1", "ACTION2", "h3", changed_cells=5.0, transforms=["translate"])
    cf = CounterfactualSimulator(model)
    result = cf.simulate("g1", "h1", "ACTION1", "ACTION2")
    assert result.alt_action == "ACTION2"
    assert result.predicted_changed_cells == 5.0
    assert result.source in {"observed", "model"}


def test_semantics_store_ingest():
    store = SemanticsStore()
    t = _transition(3, action="ACTION3")
    sig = store.ingest_transition(t)
    assert sig is not None
    meta = t["metadata"]["causality"]
    assert "semantic_label" in meta
    assert "uncertainty" in meta


def test_change_analyzer_grid():
    analyzer = ChangeAnalyzer()
    before = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
    after = [[0, 0, 0], [0, 1, 0], [0, 0, 2]]
    report = analyzer.analyze(before, after, prev_hash="a", next_hash="b")
    assert report.num_changed_cells == 1
    assert report.graph_edge_created is True
