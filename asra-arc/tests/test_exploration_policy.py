from asra.exploration.exploration_graph import ExplorationGraph
from asra.exploration.policy_v2 import ExplorationPolicyV2
from asra.exploration.visitation_memory import VisitationMemory


def test_policy_prefers_unexplored_action():
    policy = ExplorationPolicyV2()
    graph = ExplorationGraph()
    memory = VisitationMemory()
    memory.observe("s0", step=0)
    decision = policy.select_action("s0", ["left", "forward"], graph, memory)
    assert decision["selected_action"] in {"left", "forward"}
    assert decision["score"] > 0


def test_parse_babyai_goto_mission():
    from asra.exploration.subgoals import parse_babyai_mission

    subgoals = parse_babyai_mission("go to the red ball")
    assert len(subgoals) >= 1
    assert subgoals[0].subgoal_id == "goto_target"
