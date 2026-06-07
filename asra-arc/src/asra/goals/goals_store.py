from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from asra.goals.experiment_planner import ExperimentPlanner
from asra.goals.goal_hypothesis_generator import GoalHypothesisGenerator
from asra.goals.hypothesis_ranker import HypothesisRanker
from asra.goals.object_role_classifier import ObjectRoleClassifier
from asra.goals.progress_detector import ProgressDetector
from asra.goals.schemas import GoalHypothesis, ProgressSignal


class GoalsStore:
    def __init__(self) -> None:
        self.generator = GoalHypothesisGenerator()
        self.progress = ProgressDetector()
        self.roles = ObjectRoleClassifier()
        self.ranker = HypothesisRanker()
        self.planner = ExperimentPlanner()
        self.hypotheses: dict[str, list[GoalHypothesis]] = {}
        self.progress_log: list[ProgressSignal] = []

    def ensure_game_hypotheses(self, game_id: str, scene: dict[str, Any]) -> list[GoalHypothesis]:
        if game_id not in self.hypotheses:
            role_map = self.roles.roles_dict(scene)
            self.hypotheses[game_id] = self.generator.generate(
                game_id, scene, object_roles=role_map
            )
        return self.hypotheses[game_id]

    def ingest_transition(self, transition: dict[str, Any]) -> dict[str, Any]:
        game_id = str(transition.get("game_id") or "unknown")
        episode_id = str(transition.get("episode_id") or "unknown")
        step = int(transition.get("step") or 0)
        state = transition.get("state") or {}
        state_hash = str(state.get("state_hash") or "")
        action = str((transition.get("action") or {}).get("name") or "")
        reward = float(transition.get("reward") or 0)
        diff = transition.get("diff") or {}
        meta = transition.get("metadata") or {}
        scene = (diff.get("object_scene_after") or state.get("object_scene") or {})
        causality = meta.get("causality") or {}
        semantic_label = str(causality.get("semantic_label") or "unknown")
        level_completed = int(meta.get("levels_completed") or transition.get("levels_completed") or 0)
        terminal_win = bool(transition.get("terminal") and transition.get("terminal_state") == "WIN")

        hyps = self.ensure_game_hypotheses(game_id, scene if isinstance(scene, dict) else {})
        signals = self.progress.detect(
            episode_id=episode_id,
            step=step,
            state_hash=state_hash,
            action=action,
            reward=reward,
            level_completed=level_completed,
            semantic_label=semantic_label,
            diff=diff if isinstance(diff, dict) else {},
            terminal_win=terminal_win,
        )
        self.progress_log.extend(signals)
        for h in hyps:
            for sig in signals:
                self.ranker.update_from_signal(h, sig)
            self.ranker.refute_mismatch(h, semantic_label, reward > 0)
        ranked = self.ranker.rank(hyps)
        leading = ranked[0] if ranked else None
        goals_meta = {
            "leading_hypothesis_id": leading.hypothesis_id if leading else None,
            "leading_template_id": leading.template_id if leading else None,
            "progress_score": leading.progress_score if leading else 0.0,
            "object_roles": self.roles.roles_dict(scene if isinstance(scene, dict) else {}),
        }
        transition.setdefault("metadata", {})["goals"] = goals_meta
        return transition

    def save(self, output_dir: str | Path) -> dict[str, Path]:
        root = Path(output_dir)
        hyp_dir = root / "hypotheses"
        hyp_dir.mkdir(parents=True, exist_ok=True)
        paths: dict[str, Path] = {}
        for game_id, hyps in self.hypotheses.items():
            path = hyp_dir / f"{game_id}.json"
            path.write_text(
                json.dumps([h.to_dict() for h in hyps], indent=2),
                encoding="utf-8",
            )
            paths[game_id] = path
        prog_path = root / "progress_events.json"
        prog_path.write_text(
            json.dumps([s.to_dict() for s in self.progress_log], indent=2),
            encoding="utf-8",
        )
        paths["progress_events"] = prog_path
        return paths
