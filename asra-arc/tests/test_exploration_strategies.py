from asra.exploration.schemas import StrategyPattern
from asra.exploration.strategies import StrategyLibrary


def test_strategy_library_match_and_bias() -> None:
    lib = StrategyLibrary()
    lib.add(
        StrategyPattern(
            strategy_id="door_key_sequence_v1",
            name="door_key_sequence",
            precondition={"env_type": "doorkey", "has_key": False, "door_open": False},
            action_sequence=["ACTION3", "ACTION4", "ACTION6"],
            success_count=1,
            source_env="MiniGrid-DoorKey-8x8-v0",
        )
    )
    pre = {"env_type": "doorkey", "has_key": False, "door_open": False}
    assert lib.bias_for_state(pre) == ["ACTION3"]
    assert lib.strategy_hint(pre) == "door_key_sequence_v1"


def test_strategy_extract_from_success_episode() -> None:
    lib = StrategyLibrary()
    transitions = [
        {
            "action": {"name": "ACTION3"},
            "next_state": {"status": "NOT_FINISHED"},
        },
        {
            "action": {"name": "ACTION4"},
            "next_state": {"status": "WIN"},
        },
    ]
    pattern = lib.extract_from_episode(
        transitions,
        {"env_type": "doorkey", "has_key": False},
        "MiniGrid-DoorKey-8x8-v0",
    )
    assert pattern is not None
    assert pattern.action_sequence == ["ACTION3", "ACTION4"]
