from __future__ import annotations


def reward_summary(transitions: list[dict]) -> dict:
    rewards = [float(row.get("reward", 0.0)) for row in transitions]
    return {"total_reward": sum(rewards), "mean_reward": sum(rewards) / len(rewards) if rewards else 0.0, "positive_rewards": sum(1 for reward in rewards if reward > 0)}
