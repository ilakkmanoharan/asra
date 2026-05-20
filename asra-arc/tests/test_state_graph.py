from asra.memory.state_graph import StateGraph


def transition(action="ACTION1"):
    return {
        "state": {"state_hash": "a", "grid": [[0]], "status": "NOT_FINISHED"},
        "next_state": {"state_hash": "b", "grid": [[1]], "status": "NOT_FINISHED"},
        "action": {"name": action},
        "reward": 0.0,
        "terminal_state": False,
        "diff": {"num_changed_cells": 1, "change_ratio": 1.0},
    }


def test_adds_nodes_and_edges():
    graph = StateGraph()
    graph.add_transition(transition())
    payload = graph.to_dict()
    assert set(payload["nodes"]) == {"a", "b"}
    assert len(payload["edges"]) == 1


def test_increments_edge_count_and_visit_count():
    graph = StateGraph()
    graph.add_transition(transition())
    graph.add_transition(transition())
    payload = graph.to_dict()
    assert payload["edges"][0]["count"] == 2
    assert payload["nodes"]["a"]["visit_count"] == 2
