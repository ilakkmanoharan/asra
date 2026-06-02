from asra.exploration.replay import TransitionReplayBuffer


def test_replay_buffer_keeps_high_priority():
    buf = TransitionReplayBuffer(capacity=2)
    buf.push({"id": "low"}, 0.1)
    buf.push({"id": "high"}, 0.9)
    buf.push({"id": "mid"}, 0.5)
    sampled = buf.sample(2)
    ids = {row["id"] for row in sampled}
    assert "high" in ids
