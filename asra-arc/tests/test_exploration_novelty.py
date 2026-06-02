from asra.exploration.novelty import NoveltyScorer
from asra.exploration.visitation_memory import VisitationMemory


def test_state_novelty_decreases_with_visits():
    mem = VisitationMemory()
    scorer = NoveltyScorer()
    mem.observe("s1", step=1)
    n1 = scorer.state_novelty("s1", mem)
    mem.observe("s1", step=2)
    n2 = scorer.state_novelty("s1", mem)
    assert n2 < n1


def test_edge_novelty_penalizes_dead_end():
    mem = VisitationMemory()
    scorer = NoveltyScorer()
    good = scorer.edge_novelty("new_state", mem, reward=1.0, dead_end=False)
    bad = scorer.edge_novelty("new_state", mem, reward=0.0, dead_end=True)
    assert good > bad
