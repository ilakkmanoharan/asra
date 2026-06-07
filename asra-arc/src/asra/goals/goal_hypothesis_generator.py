from __future__ import annotations

from typing import Any

from asra.goals.schemas import GoalHypothesis

GOAL_TEMPLATES: list[dict[str, Any]] = [
    {
        "template_id": "move_to_target",
        "description": "Move an agent or object to a target region",
        "preferred_semantics": ["translate", "localized_transform"],
        "progress_weights": {"translate": 1.0, "reward": 2.0, "level_up": 3.0},
    },
    {
        "template_id": "match_pattern",
        "description": "Transform grid to match a goal pattern",
        "preferred_semantics": ["recolor", "localized_transform", "multi_cell_transform"],
        "progress_weights": {"recolor": 1.2, "reward": 2.0, "level_up": 3.0},
    },
    {
        "template_id": "collect_tokens",
        "description": "Collect or remove token objects",
        "preferred_semantics": ["delete_object", "translate"],
        "progress_weights": {"delete_object": 1.5, "reward": 2.0, "level_up": 3.0},
    },
    {
        "template_id": "unlock_passage",
        "description": "Unlock a passage or gate",
        "preferred_semantics": ["create_object", "recolor", "translate"],
        "progress_weights": {"create_object": 1.0, "recolor": 0.8, "reward": 2.5, "level_up": 3.0},
    },
    {
        "template_id": "avoid_hazard",
        "description": "Avoid hazards while making progress",
        "preferred_semantics": ["translate", "no_op"],
        "progress_weights": {"no_op": 0.2, "translate": 0.8, "reward": 2.0, "level_up": 3.0},
    },
    {
        "template_id": "transform_to_goal",
        "description": "Apply transforms until goal structure reached",
        "preferred_semantics": ["multi_cell_transform", "recolor", "create_object"],
        "progress_weights": {"multi_cell_transform": 1.3, "reward": 2.0, "level_up": 3.0},
    },
]

ARC_TEMPLATE_PRIORS: dict[str, str] = {
    "recolor": "match_pattern",
    "translate": "move_to_target",
    "compose": "transform_to_goal",
    "fill": "match_pattern",
    "crop": "transform_to_goal",
}


class GoalHypothesisGenerator:
    def __init__(self) -> None:
        self._counter = 0

    def _next_id(self, template_id: str) -> str:
        self._counter += 1
        return f"gh_{self._counter}_{template_id}"

    def generate(
        self,
        game_id: str,
        scene: dict[str, Any],
        *,
        arc_rule_family: str | None = None,
        object_roles: dict[str, str] | None = None,
    ) -> list[GoalHypothesis]:
        n_obj = int(scene.get("num_objects", 0))
        hypotheses: list[GoalHypothesis] = []
        for template in GOAL_TEMPLATES:
            if template["template_id"] == "collect_tokens" and n_obj < 2:
                continue
            hid = self._next_id(template["template_id"])
            prior = 0.5
            if arc_rule_family and ARC_TEMPLATE_PRIORS.get(arc_rule_family) == template["template_id"]:
                prior = 0.85
            hypotheses.append(
                GoalHypothesis(
                    hypothesis_id=hid,
                    game_id=game_id,
                    template_id=template["template_id"],
                    description=template["description"],
                    preferred_semantics=list(template["preferred_semantics"]),
                    progress_weights=dict(template["progress_weights"]),
                    object_roles=dict(object_roles or {}),
                    preconditions={"min_objects": 1 if n_obj else 0},
                    confidence=prior,
                )
            )
        return hypotheses
