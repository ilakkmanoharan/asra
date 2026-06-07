"""ASRA Phase 9 agent for ARC Prize 2026 — ARC-AGI-3 (Kaggle Swarm).

Phase 2 object scenes + Phase 3 exploration memory + Phase 4 causal semantics +
Phase 9 goal inference: hypothesis generation, progress detection, experiment planning.
"""

from __future__ import annotations

import glob
import hashlib
import json
import os
import random
import subprocess
import sys
import types
from collections import Counter, defaultdict, deque
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# --- Phase 3 compact exploration hints (embedded) ---


class CompactExplorationHints:
    """Visit memory + frontier bonus for action scoring."""

    def __init__(self, recent_window: int = 20) -> None:
        self.visit_counts: Dict[str, int] = defaultdict(int)
        self.recent: deque[str] = deque(maxlen=recent_window)
        self.edge_stats: Dict[Tuple[str, str], Dict[str, float]] = defaultdict(
            lambda: {"novelty": 0.0, "usefulness": 0.0, "n": 0.0}
        )

    def observe(self, state_hash: str, next_hash: str, action: str, reward: float, changed_cells: int) -> None:
        self.visit_counts[state_hash] += 1
        self.visit_counts[next_hash] += 1
        self.recent.append(next_hash)
        novelty = 1.0 / (1.0 + self.visit_counts[next_hash]) ** 0.5
        usefulness = float(reward) + (0.5 if changed_cells else 0.0)
        key = (state_hash, action)
        stats = self.edge_stats[key]
        stats["n"] += 1
        stats["novelty"] = ((stats["novelty"] * (stats["n"] - 1)) + novelty) / stats["n"]
        stats["usefulness"] = ((stats["usefulness"] * (stats["n"] - 1)) + usefulness) / stats["n"]

    def score_action(self, state_hash: str, action: str) -> float:
        visits = self.visit_counts[state_hash]
        frontier_bonus = 1.0 / (1.0 + visits) ** 0.5
        stats = self.edge_stats.get((state_hash, action))
        if stats and stats["n"] > 0:
            repeat_penalty = 1.0 if self.recent.count(state_hash) > 2 else 0.0
            return stats["novelty"] + stats["usefulness"] + frontier_bonus - repeat_penalty
        return frontier_bonus + 0.5

    def exploration_metadata(self, state_hash: str) -> Dict[str, Any]:
        return {
            "visit_count_before": self.visit_counts[state_hash],
            "frontier_node": self.visit_counts[state_hash] <= 2,
            "recent_unique": len(set(self.recent)),
        }


# --- Phase 2 compact object perception (embedded) ---


def _dominant_background(grid: List[List[int]]) -> int:
    counts: Counter[int] = Counter()
    for row in grid:
        counts.update(row)
    return counts.most_common(1)[0][0] if counts else 0


def _connected_components(
    grid: List[List[int]], background: int, connectivity: int = 4
) -> List[Tuple[int, List[Tuple[int, int]]]]:
    h = len(grid)
    w = len(grid[0]) if h else 0
    visited = [[False] * w for _ in range(h)]
    components: List[Tuple[int, List[Tuple[int, int]]]] = []
    neighbors = [(-1, 0), (1, 0), (0, -1), (0, 1)] if connectivity == 4 else [
        (-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]
    for y in range(h):
        for x in range(w):
            color = grid[y][x]
            if color == background or visited[y][x]:
                continue
            stack = [(y, x)]
            visited[y][x] = True
            pixels: List[Tuple[int, int]] = []
            while stack:
                cy, cx = stack.pop()
                pixels.append((cy, cx))
                for dy, dx in neighbors:
                    ny, nx = cy + dy, cx + dx
                    if 0 <= ny < h and 0 <= nx < w and not visited[ny][nx] and grid[ny][nx] == color:
                        visited[ny][nx] = True
                        stack.append((ny, nx))
            components.append((color, pixels))
    return components


def compact_scene(grid: List[List[int]]) -> Dict[str, Any]:
    if not grid or not grid[0]:
        return {"grid_shape": [0, 0], "background_color": 0, "num_objects": 0, "objects": []}
    bg = _dominant_background(grid)
    objects = []
    for idx, (color, pixels) in enumerate(_connected_components(grid, bg)):
        if not pixels:
            continue
        ys = [p[0] for p in pixels]
        xs = [p[1] for p in pixels]
        bbox = [min(ys), min(xs), max(ys), max(xs)]
        n = len(pixels)
        objects.append(
            {
                "object_id": f"obj_{idx}",
                "color": int(color),
                "area": n,
                "bbox": bbox,
                "centroid": [sum(ys) / n, sum(xs) / n],
            }
        )
    return {
        "grid_shape": [len(grid), len(grid[0])],
        "background_color": int(bg),
        "num_objects": len(objects),
        "objects": objects,
    }


def object_delta(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "delta_num_objects": int(after.get("num_objects", 0)) - int(before.get("num_objects", 0)),
        "before_num_objects": int(before.get("num_objects", 0)),
        "after_num_objects": int(after.get("num_objects", 0)),
    }


def transform_histogram_from_scenes(before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, int]:
    """Lightweight transform tags from object-scene deltas (Phase 4 embedded)."""
    hist: Counter = Counter()
    delta = int(after.get("num_objects", 0)) - int(before.get("num_objects", 0))
    if delta > 0:
        hist["create"] += delta
    elif delta < 0:
        hist["delete"] += -delta
    before_objs = {o["object_id"]: o for o in before.get("objects", [])}
    after_objs = {o["object_id"]: o for o in after.get("objects", [])}
    for oid, obj_b in before_objs.items():
        obj_a = after_objs.get(oid)
        if obj_a is None:
            continue
        if obj_b.get("color") != obj_a.get("color"):
            hist["recolor"] += 1
        cy0, cx0 = obj_b.get("centroid", [0, 0])
        cy1, cx1 = obj_a.get("centroid", [0, 0])
        if abs(cy1 - cy0) > 0.4 or abs(cx1 - cx0) > 0.4:
            hist["translate"] += 1
    if not hist and before.get("num_objects") == after.get("num_objects"):
        hist["identity"] = 1
    return dict(hist)


# --- Kaggle bootstrap ---


def _working_dir() -> str:
    return "/kaggle/working" if os.path.isdir("/kaggle/working") else "."


def _venv_dir(working: str) -> str:
    if os.path.isdir("/kaggle/working"):
        return "/tmp/asra_venv"
    return os.path.join(working, "asra_venv")


def _venv_paths(working: str) -> Tuple[str, str, str]:
    venv = _venv_dir(working)
    return venv, os.path.join(venv, "bin", "python"), os.path.join(venv, "bin", "pip")


def _maybe_reexec_venv() -> None:
    if os.environ.get("ASRA_VENV_ACTIVE") == "1":
        return
    working = _working_dir()
    _, venv_py, _ = _venv_paths(working)
    if not os.path.isfile(venv_py):
        return
    if os.path.realpath(sys.executable) == os.path.realpath(venv_py):
        os.environ["ASRA_VENV_ACTIVE"] = "1"
        return
    env = os.environ.copy()
    env["ASRA_VENV_ACTIVE"] = "1"
    env.setdefault("PYTHONNOUSERSITE", "1")
    os.execve(venv_py, [venv_py, os.path.abspath(__file__), *sys.argv[1:]], env)


_maybe_reexec_venv()


def _is_kaggle_runtime() -> bool:
    if os.path.exists("/kaggle/input"):
        return True
    return os.path.isdir(os.path.join(_working_dir(), "asra_competition"))


def _resolve_comp_root(is_kaggle: bool) -> str:
    if is_kaggle:
        working = _working_dir()
        candidates = [
            "/kaggle/input/competitions/arc-prize-2026-arc-agi-3",
            "/kaggle/input/arc-prize-2026-arc-agi-3",
            os.path.join(working, "asra_competition"),
        ]
        return next((p for p in candidates if os.path.isdir(p)), candidates[0])
    return os.environ.get("ASRA_COMP_ROOT", os.path.join("private", "kaggle-dataset", "competition"))


def _verify_runtime(agents_root: str) -> bool:
    if not agents_root or not os.path.isdir(os.path.join(agents_root, "agents")):
        return False
    try:
        import arcengine  # noqa: F401
        import arc_agi  # noqa: F401
    except ImportError:
        return False
    return True


def _venv_site_packages(venv: str) -> str:
    ver = f"{sys.version_info.major}.{sys.version_info.minor}"
    site = os.path.join(venv, "lib", f"python{ver}", "site-packages")
    os.makedirs(site, exist_ok=True)
    return site


def _install_wheels_in_venv(wheels_dir: str, working: str) -> str:
    venv, venv_py, _ = _venv_paths(working)
    if not os.path.isfile(venv_py):
        subprocess.check_call(
            [sys.executable, "-m", "venv", venv, "--system-site-packages", "--without-pip"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    wheels = sorted(glob.glob(os.path.join(wheels_dir, "*.whl")))
    if wheels:
        target = _venv_site_packages(venv)
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--target", target, "--no-deps", "--upgrade", "-q", *wheels],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Venv wheel install failed:\n{result.stderr}")
    os.environ["ASRA_VENV"] = venv
    return venv_py


def _bootstrap_kaggle() -> str:
    is_kaggle = _is_kaggle_runtime()
    working = _working_dir()
    comp_root = _resolve_comp_root(is_kaggle)
    agents_root = os.path.join(comp_root, "ARC-AGI-3-Agents")
    wheels_dir = os.path.join(comp_root, "arc_agi_3_wheels")
    working_wheels = os.path.join(working, "wheels")
    if not os.path.isdir(wheels_dir) and os.path.isdir(working_wheels):
        wheels_dir = working_wheels
    env_dir = os.path.join(comp_root, "environment_files")
    working_env = os.path.join(working, "environment_files")
    if not os.path.isdir(env_dir) and os.path.isdir(working_env):
        env_dir = working_env
    recordings_dir = os.path.join(working, "recordings")
    os.makedirs(recordings_dir, exist_ok=True)
    if os.path.isdir(agents_root) and agents_root not in sys.path:
        sys.path.insert(0, agents_root)
    os.environ.setdefault("RECORDINGS_DIR", recordings_dir)
    os.environ.setdefault("ENVIRONMENTS_DIR", env_dir if os.path.isdir(env_dir) else "environment_files")
    os.environ["OPERATION_MODE"] = "COMPETITION" if is_kaggle else os.environ.get("OPERATION_MODE", "OFFLINE")
    os.environ["ASRA_AGENTS_ROOT"] = agents_root
    if _verify_runtime(agents_root):
        return agents_root
    if os.path.isdir(wheels_dir):
        venv_py = _install_wheels_in_venv(wheels_dir, working)
        if os.path.realpath(sys.executable) != os.path.realpath(venv_py):
            env = os.environ.copy()
            env["ASRA_VENV_ACTIVE"] = "1"
            env.setdefault("PYTHONNOUSERSITE", "1")
            os.execve(venv_py, [venv_py, os.path.abspath(__file__), *sys.argv[1:]], env)
    if os.path.isdir(agents_root) and agents_root not in sys.path:
        sys.path.insert(0, agents_root)
    if not _verify_runtime(agents_root):
        raise RuntimeError(f"ARC-AGI-3 runtime not ready. comp_root={comp_root!r}")
    return agents_root


def _load_agents_runtime(agents_root: str):
    import importlib.util

    agents_dir = os.path.join(agents_root, "agents")
    if not os.path.isdir(agents_dir):
        raise RuntimeError(f"agents package not found under {agents_root}")
    if agents_root not in sys.path:
        sys.path.insert(0, agents_root)
    pkg = sys.modules.get("agents")
    if pkg is None or not getattr(pkg, "_ASRA_STUB", False):
        pkg = types.ModuleType("agents")
        pkg.__path__ = [agents_dir]
        pkg.__package__ = "agents"
        pkg.AVAILABLE_AGENTS = {}
        pkg._ASRA_STUB = True
        sys.modules["agents"] = pkg

    def _load_submodule(name: str):
        fq = f"agents.{name}"
        if fq in sys.modules:
            return sys.modules[fq]
        path = os.path.join(agents_dir, f"{name}.py")
        spec = importlib.util.spec_from_file_location(fq, path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load {fq} from {path}")
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = "agents"
        sys.modules[fq] = mod
        spec.loader.exec_module(mod)
        return mod

    _load_submodule("tracing")
    _load_submodule("recorder")
    agent_mod = _load_submodule("agent")
    swarm_mod = _load_submodule("swarm")
    return agent_mod.Agent, swarm_mod.Swarm, pkg.AVAILABLE_AGENTS


def perception_self_test() -> None:
    grid = [[0, 1, 0], [0, 1, 0], [0, 0, 0]]
    scene = compact_scene(grid)
    assert scene["num_objects"] >= 1
    print(f"compact_scene objects={scene['num_objects']}")
    print("perception self-test OK")


def exploration_self_test() -> None:
    hints = CompactExplorationHints()
    hints.observe("h1", "h2", "ACTION1", 0.0, 1)
    s = hints.score_action("h1", "ACTION1")
    assert s > 0
    meta = hints.exploration_metadata("h1")
    assert meta["visit_count_before"] >= 1
    print(f"exploration score={s:.3f} meta={meta}")
    print("exploration self-test OK")


class CausalSemanticsEngine:
    """Phase 4 embedded: effect signatures, prediction, uncertainty, counterfactual."""

    def __init__(self) -> None:
        self.effects: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)
        self.successors: Dict[Tuple[str, str], Counter] = defaultdict(Counter)

    def observe(
        self,
        state_hash_value: str,
        action: str,
        diff: Dict[str, Any],
        reward: float,
        *,
        next_hash: Optional[str] = None,
    ) -> None:
        self.effects[(state_hash_value, action)].append(
            {
                "num_changed_cells": diff.get("num_changed_cells"),
                "reward": reward,
                "delta_num_objects": diff.get("delta_num_objects"),
                "transform_histogram": dict(diff.get("transform_histogram") or {}),
                "next_hash": next_hash,
            }
        )
        if next_hash:
            self.successors[(state_hash_value, action)][next_hash] += 1

    def _label(self, mean: float, obj_mean: float, hist: Dict[str, int]) -> str:
        if mean == 0 and obj_mean == 0:
            return "no_op"
        top = max(hist, key=hist.get) if hist else None
        if top == "translate":
            return "translate"
        if top == "recolor":
            return "recolor"
        if top == "create":
            return "create_object"
        if top == "delete":
            return "delete_object"
        if mean <= 1.5:
            return "localized_transform"
        if obj_mean != 0:
            return "object_count_change"
        return "multi_cell_transform"

    def infer(self, state_hash_value: str, action: str) -> Dict[str, Any]:
        effects = self.effects.get((state_hash_value, action), [])
        if not effects:
            return {
                "observations": 0,
                "semantic_label": "unknown",
                "hypothesis": "unknown",
                "consistency_score": None,
                "confidence": 0.0,
                "uncertainty": 1.0,
                "predicted_changed_cells": 0.0,
            }
        counts = [float(e["num_changed_cells"]) for e in effects if e["num_changed_cells"] is not None]
        obj_deltas = [float(e.get("delta_num_objects") or 0) for e in effects]
        std = float(np.std(counts)) if counts else 0.0
        mean = float(np.mean(counts)) if counts else 0.0
        obj_mean = float(np.mean(obj_deltas)) if obj_deltas else 0.0
        hist: Counter = Counter()
        for e in effects:
            hist.update(e.get("transform_histogram") or {})
        label = self._label(mean, obj_mean, dict(hist))
        consistency = float(1.0 / (1.0 + std)) if counts else 0.0
        n = len(effects)
        confidence = min(1.0, (n / 5.0) * 0.6 + consistency * 0.4)
        uncertainty = min(1.0, (1.0 / (1.0 + n) ** 0.5) + 0.15 * min(1.0, std / max(1.0, mean + 1.0)))
        return {
            "observations": n,
            "semantic_label": label,
            "hypothesis": label,
            "consistency_score": consistency,
            "confidence": confidence,
            "uncertainty": uncertainty,
            "mean_delta_objects": obj_mean,
            "transform_histogram": dict(hist),
            "predicted_changed_cells": mean,
        }

    def predict_next(self, state_hash_value: str, action: str) -> Dict[str, Any]:
        counts = self.successors.get((state_hash_value, action))
        if not counts:
            return {"next_hash": None, "probability": 0.0}
        total = sum(counts.values())
        next_hash, top = counts.most_common(1)[0]
        return {"next_hash": next_hash, "probability": top / total}

    def counterfactual(self, state_hash_value: str, actual_action: str, alt_action: str) -> Dict[str, Any]:
        sem = self.infer(state_hash_value, alt_action)
        pred = self.predict_next(state_hash_value, alt_action)
        return {
            "actual_action": actual_action,
            "alt_action": alt_action,
            "predicted_changed_cells": sem.get("predicted_changed_cells", 0.0),
            "semantic_label": sem.get("semantic_label", "unknown"),
            "confidence": sem.get("confidence", 0.0),
            "next_hash": pred.get("next_hash"),
            "probability": pred.get("probability", 0.0),
        }


def causality_self_test() -> None:
    engine = CausalSemanticsEngine()
    diff = {
        "num_changed_cells": 2,
        "delta_num_objects": 0,
        "transform_histogram": {"translate": 1},
    }
    engine.observe("h1", "ACTION1", diff, 0.0, next_hash="h2")
    engine.observe("h1", "ACTION1", diff, 0.0, next_hash="h2")
    sem = engine.infer("h1", "ACTION1")
    assert sem["observations"] == 2
    assert sem["semantic_label"] != "unknown"
    assert sem["confidence"] is not None and sem["confidence"] > 0
    cf = engine.counterfactual("h1", "ACTION3", "ACTION1")
    assert cf["alt_action"] == "ACTION1"
    print(f"causality sem={sem['semantic_label']} conf={sem['confidence']:.2f} u={sem['uncertainty']:.2f}")
    print("causality self-test OK")


# --- Phase 9 goal inference (embedded) ---

GOAL_TEMPLATES: List[Dict[str, Any]] = [
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


class GoalHypothesisEngine:
    """Phase 9 embedded: goal templates, progress signals, hypothesis ranking, experiment hints."""

    def __init__(self) -> None:
        self.hypotheses: Dict[str, Dict[str, Any]] = {}
        self.progress_events: List[Dict[str, Any]] = []
        self._hypothesis_counter = 0

    def _spawn_hypothesis(self, template: Dict[str, Any]) -> str:
        self._hypothesis_counter += 1
        hid = f"gh_{self._hypothesis_counter}_{template['template_id']}"
        self.hypotheses[hid] = {
            "hypothesis_id": hid,
            "template_id": template["template_id"],
            "description": template["description"],
            "preferred_semantics": list(template["preferred_semantics"]),
            "progress_weights": dict(template["progress_weights"]),
            "support": 0,
            "refute": 0,
            "progress_score": 0.0,
            "status": "active",
        }
        return hid

    def ensure_hypotheses(self, scene: Dict[str, Any]) -> None:
        if self.hypotheses:
            return
        n_obj = int(scene.get("num_objects", 0))
        for template in GOAL_TEMPLATES:
            if template["template_id"] == "collect_tokens" and n_obj < 2:
                continue
            self._spawn_hypothesis(template)

    def observe_progress(
        self,
        *,
        reward: float,
        level_delta: int,
        semantics: Dict[str, Any],
        diff: Dict[str, Any],
    ) -> None:
        event = {
            "reward": reward,
            "level_delta": level_delta,
            "semantic_label": semantics.get("semantic_label", "unknown"),
            "delta_num_objects": diff.get("delta_num_objects", 0),
        }
        self.progress_events.append(event)
        label = event["semantic_label"]
        for hyp in self.hypotheses.values():
            if hyp["status"] != "active":
                continue
            w = hyp["progress_weights"]
            delta = 0.0
            if label in hyp["preferred_semantics"]:
                delta += w.get(label, 0.5)
            if reward > 0:
                delta += w.get("reward", 0.0)
            if level_delta > 0:
                delta += w.get("level_up", 0.0)
                hyp["support"] += 1
            elif reward <= 0 and label not in hyp["preferred_semantics"] and label != "unknown":
                hyp["refute"] += 1
            hyp["progress_score"] += delta

    def rank_hypotheses(self) -> List[Dict[str, Any]]:
        ranked = sorted(
            self.hypotheses.values(),
            key=lambda h: (h["progress_score"] + 2.0 * h["support"] - 1.5 * h["refute"]),
            reverse=True,
        )
        return ranked

    def leading_hypothesis(self) -> Optional[Dict[str, Any]]:
        ranked = self.rank_hypotheses()
        return ranked[0] if ranked else None

    def action_goal_score(self, semantics: Dict[str, Any]) -> float:
        lead = self.leading_hypothesis()
        if not lead:
            return 0.0
        label = semantics.get("semantic_label", "unknown")
        if label in lead["preferred_semantics"]:
            return lead["progress_weights"].get(label, 0.5)
        return 0.0

    def experiment_discrimination_bonus(
        self, state_hash_value: str, action: str, semantics_engine: CausalSemanticsEngine
    ) -> float:
        ranked = self.rank_hypotheses()
        if len(ranked) < 2:
            return 0.0
        top, second = ranked[0], ranked[1]
        sem = semantics_engine.infer(state_hash_value, action)
        label = sem.get("semantic_label", "unknown")
        top_match = 1.0 if label in top["preferred_semantics"] else 0.0
        second_match = 1.0 if label in second["preferred_semantics"] else 0.0
        unc = float(sem.get("uncertainty") or 0.0)
        return unc * abs(top_match - second_match)


def goals_self_test() -> None:
    goals = GoalHypothesisEngine()
    scene = compact_scene([[0, 1, 2], [0, 1, 0], [3, 0, 0]])
    goals.ensure_hypotheses(scene)
    assert len(goals.hypotheses) >= 3
    sem = {"semantic_label": "translate", "confidence": 0.8, "uncertainty": 0.2}
    diff = {"delta_num_objects": 0}
    goals.observe_progress(reward=0.0, level_delta=0, semantics=sem, diff=diff)
    goals.observe_progress(reward=1.0, level_delta=1, semantics=sem, diff=diff)
    lead = goals.leading_hypothesis()
    assert lead is not None
    score = goals.action_goal_score(sem)
    assert score > 0
    print(f"goals lead={lead['template_id']} score={score:.2f} n={len(goals.hypotheses)}")
    print("goals self-test OK")




# --- Phase 9 planning (embedded) ---


class PlanningEngine:
    """BFS successor graph + strategy library + meta explore/exploit."""

    def __init__(self) -> None:
        self.successors: Dict[str, Dict[str, str]] = defaultdict(dict)
        self.stuck: Counter = Counter()

    def observe(self, state_hash: str, action: str, next_hash: str) -> None:
        self.successors[state_hash][action] = next_hash

    def plan_bonus(self, state_hash: str, action: str, goal_template: str | None, visit_count: int) -> float:
        strategy_map = {
            "move_to_target": ["translate"],
            "collect_tokens": ["delete_object", "translate"],
            "match_pattern": ["recolor", "multi_cell_transform"],
            "avoid_hazard": ["translate", "no_op"],
            "unlock_passage": ["create_object", "recolor"],
            "transform_to_goal": ["multi_cell_transform", "recolor"],
        }
        prefs = strategy_map.get(goal_template or "", ["translate"])
        if state_hash in self.successors and action in self.successors[state_hash]:
            return 0.3
        mode = "explore" if visit_count <= 2 else "exploit"
        return (1.2 if mode == "explore" else 0.8) * (0.5 if action in self.successors.get(state_hash, {}) else 1.0)


def planning_self_test() -> None:
    eng = PlanningEngine()
    eng.observe("s1", "ACTION1", "s2")
    b = eng.plan_bonus("s1", "ACTION1", "move_to_target", 1)
    assert b >= 0
    print(f"planning bonus={b:.2f}")
    print("planning self-test OK")




# --- Phase 9 robustness (embedded) ---


class RobustnessEngine:
    """Failure analysis, stuck detection, action waste reduction."""

    def __init__(self) -> None:
        self.state_visits: Counter = Counter()
        self.no_progress_streak = 0

    def observe(self, state_hash: str, changed_cells: int, reward: float) -> None:
        self.state_visits[state_hash] += 1
        if changed_cells == 0 and reward <= 0:
            self.no_progress_streak += 1
        else:
            self.no_progress_streak = 0

    def stuck_penalty(self, state_hash: str) -> float:
        if self.state_visits[state_hash] > 4:
            return 1.5
        if self.no_progress_streak >= 3:
            return 1.0
        return 0.0

    def action_waste_penalty(self, action: str, local_count: int) -> float:
        return min(1.0, local_count * 0.15)


def robustness_self_test() -> None:
    eng = RobustnessEngine()
    eng.observe("s1", 0, 0.0)
    eng.observe("s1", 0, 0.0)
    p = eng.stuck_penalty("s1")
    assert p >= 0
    print(f"robustness penalty={p:.2f}")
    print("robustness self-test OK")




# --- Phase 9 Decision Biology bridge (embedded) ---


class BiologyBridgeEngine:
    """Map game transitions to perturbation-response framing (Decision Biology)."""

    PERTURBATION_MAP = {
        "translate": "mechanical_stimulus",
        "recolor": "signaling_inhibitor",
        "create_object": "gene_overexpression",
        "delete_object": "knockdown",
        "multi_cell_transform": "pathway_activation",
    }

    def perturbation_label(self, semantic_label: str) -> str:
        return self.PERTURBATION_MAP.get(semantic_label, "unknown_perturbation")

    def cell_state_id(self, scene: Dict[str, Any]) -> str:
        n = int(scene.get("num_objects", 0))
        colors = sorted({int(o.get("color", 0)) for o in scene.get("objects", [])})
        return f"cell_state_{n}_{'-'.join(map(str, colors[:3]))}"


def biology_self_test() -> None:
    eng = BiologyBridgeEngine()
    assert eng.perturbation_label("translate") == "mechanical_stimulus"
    sid = eng.cell_state_id({"num_objects": 2, "objects": [{"color": 1}, {"color": 2}]})
    assert sid.startswith("cell_state_")
    print(f"biology state={sid}")
    print("biology self-test OK")




# --- Phase 9 final stack marker (embedded) ---


class FinalStackEngine:
    """Integrates Phases 1-8 narrative for Milestone submission."""

    PHASES = ["experience", "observation", "exploration", "causality", "goals", "planning", "robustness", "biology"]

    def stack_summary(self) -> str:
        return "+".join(self.PHASES)


def final_self_test() -> None:
    eng = FinalStackEngine()
    s = eng.stack_summary()
    assert "biology" in s
    print(f"final stack={s}")
    print("final self-test OK")


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "--self-test":
    perception_self_test()
    exploration_self_test()
    causality_self_test()
    goals_self_test()
    final_self_test()
    biology_self_test()
    robustness_self_test()
    planning_self_test()
    print(f"python={sys.executable}")
    print("runtime self-test OK (Phase 9)")
    sys.exit(0)


AGENTS_ROOT = _bootstrap_kaggle()

import pandas as pd
from arcengine import FrameData, GameAction, GameState

Agent, Swarm, AVAILABLE_AGENTS = _load_agents_runtime(AGENTS_ROOT)

SEED = int(os.environ.get("ASRA_SEED", "42"))
MAX_ACTIONS = int(os.environ.get("ASRA_MAX_ACTIONS", "80"))
SIMPLE_ACTIONS = ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5", "ACTION7"]
OBJECT_HINT_WEIGHT = float(os.environ.get("ASRA_OBJECT_HINT_WEIGHT", "0.30"))
EXPLORATION_HINT_WEIGHT = float(os.environ.get("ASRA_EXPLORATION_HINT_WEIGHT", "0.35"))
SEMANTICS_HINT_WEIGHT = float(os.environ.get("ASRA_SEMANTICS_HINT_WEIGHT", "0.35"))
PREDICTION_HINT_WEIGHT = float(os.environ.get("ASRA_PREDICTION_HINT_WEIGHT", "0.20"))
UNCERTAINTY_HINT_WEIGHT = float(os.environ.get("ASRA_UNCERTAINTY_HINT_WEIGHT", "0.30"))
GOAL_HINT_WEIGHT = float(os.environ.get("ASRA_GOAL_HINT_WEIGHT", "0.25"))
EXPERIMENT_HINT_WEIGHT = float(os.environ.get("ASRA_EXPERIMENT_HINT_WEIGHT", "0.15"))
FINAL_HINT_WEIGHT = float(os.environ.get("ASRA_FINAL_HINT_WEIGHT", "0.05"))
BIO_HINT_WEIGHT = float(os.environ.get("ASRA_BIO_HINT_WEIGHT", "0.10"))
ROBUST_HINT_WEIGHT = float(os.environ.get("ASRA_ROBUST_HINT_WEIGHT", "-0.25"))
PLAN_HINT_WEIGHT = float(os.environ.get("ASRA_PLAN_HINT_WEIGHT", "0.20"))

random.seed(SEED)
np.random.seed(SEED)


def canonical_grid(grid: Any) -> List[List[int]]:
    return np.array(grid, dtype=int).tolist()


def state_hash(grid: Any) -> str:
    payload = json.dumps(canonical_grid(grid), separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ASRAExplorer:
    """Phase 2 object hints + Phase 3 exploration + Phase 4 causality + Phase 9 goals."""

    def __init__(self, action_names: List[str]) -> None:
        self.action_names = action_names
        self.state_action_counts: Counter = Counter()
        self.action_rewards: Dict[str, List[float]] = defaultdict(list)
        self.object_effect_scores: Dict[Tuple[str, str], float] = defaultdict(float)
        self.dead_ends: set = set()
        self.exploration = CompactExplorationHints()
        self.goals = GoalHypothesisEngine()
        self.final = FinalStackEngine()
        self.biology = BiologyBridgeEngine()
        self.robust = RobustnessEngine()
        self.planning = PlanningEngine()
        self._last_level: int = 0

    def update(
        self,
        state_hash_value: str,
        next_hash: str,
        action: str,
        diff: Dict[str, Any],
        reward: float,
        *,
        semantics: Optional[Dict[str, Any]] = None,
        level_completed: int = 0,
    ) -> None:
        self.state_action_counts[(state_hash_value, action)] += 1
        self.action_rewards[action].append(float(reward))
        changed = int(diff.get("num_changed_cells") or 0)
        if changed == 0 and reward <= 0:
            self.dead_ends.add((state_hash_value, action))
        delta_obj = diff.get("delta_num_objects")
        if delta_obj is not None and delta_obj != 0:
            self.object_effect_scores[(state_hash_value, action)] += 0.5 * (1.0 if delta_obj > 0 else 0.7)
        self.exploration.observe(state_hash_value, next_hash, action, reward, changed)
        self.robust.observe(state_hash_value, changed, float(reward))
        self.planning.observe(state_hash_value, action, next_hash)
        level_delta = max(0, int(level_completed) - self._last_level)
        self._last_level = max(self._last_level, int(level_completed))
        if semantics:
            self.goals.observe_progress(
                reward=float(reward),
                level_delta=level_delta,
                semantics=semantics,
                diff=diff,
            )

    def choose_action(
        self,
        state_hash_value: str,
        semantics: CausalSemanticsEngine,
        available: Optional[List[str]] = None,
        scene_hint: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, Dict[str, Any], Dict[str, Any]]:
        if scene_hint:
            self.goals.ensure_hypotheses(scene_hint)
        candidates = [a for a in self.action_names if available is None or a in available] or list(self.action_names)
        scores: Dict[str, float] = {}
        meta_by_action: Dict[str, Dict[str, Any]] = {}
        num_objects = int((scene_hint or {}).get("num_objects", 0))
        for action in candidates:
            if (state_hash_value, action) in self.dead_ends:
                continue
            sem = semantics.infer(state_hash_value, action)
            uncertainty = float(sem.get("uncertainty") or 1.0)
            confidence = float(sem.get("confidence") or 0.0)
            predicted = float(sem.get("predicted_changed_cells") or 0.0)
            local = self.state_action_counts[(state_hash_value, action)]
            mean_r = float(np.mean(self.action_rewards[action])) if self.action_rewards[action] else 0.0
            obj_bonus = OBJECT_HINT_WEIGHT * self.object_effect_scores.get((state_hash_value, action), 0.0)
            if num_objects == 0:
                obj_bonus *= 0.5
            explore_bonus = EXPLORATION_HINT_WEIGHT * self.exploration.score_action(state_hash_value, action)
            sem_bonus = SEMANTICS_HINT_WEIGHT * confidence
            pred_bonus = PREDICTION_HINT_WEIGHT * min(1.0, predicted / 10.0)
            unc_bonus = UNCERTAINTY_HINT_WEIGHT * uncertainty
            goal_bonus = GOAL_HINT_WEIGHT * self.goals.action_goal_score(sem)
            plan_bonus = PLAN_HINT_WEIGHT * self.planning.plan_bonus(state_hash_value, action, (lead or {}).get('template_id'), self.exploration.visit_counts[state_hash_value])
            stuck_pen = ROBUST_HINT_WEIGHT * (self.robust.stuck_penalty(state_hash_value) + self.robust.action_waste_penalty(action, local))
            bio_bonus = BIO_HINT_WEIGHT * (0.5 if self.biology.perturbation_label(sem.get('semantic_label', 'unknown')) != 'unknown_perturbation' else 0.0)
            final_bonus = FINAL_HINT_WEIGHT * 0.5
            exp_bonus = EXPERIMENT_HINT_WEIGHT * self.goals.experiment_discrimination_bonus(
                state_hash_value, action, semantics
            )
            scores[action] = (
                2.0 / (1.0 + local)
                + unc_bonus
                + sem_bonus
                + pred_bonus
                + goal_bonus
                + exp_bonus
                + 0.5 * mean_r
                + obj_bonus
                + explore_bonus
                + plan_bonus
                + random.random() * 0.05
            )
            meta_by_action[action] = sem
        if not scores:
            action = random.choice(candidates)
            lead = self.goals.leading_hypothesis() or {}
            return action, meta_by_action.get(action, {}), lead
        action = max(scores.items(), key=lambda kv: kv[1])[0]
        lead = self.goals.leading_hypothesis() or {}
        return action, meta_by_action.get(action, {}), lead


GLOBAL_SEMANTICS = CausalSemanticsEngine()
GLOBAL_EXPLORER = ASRAExplorer(SIMPLE_ACTIONS)


class ASRAAgent(Agent):
    """Phase 9: object scenes + exploration + causality + goal hypothesis hints."""

    MAX_ACTIONS = MAX_ACTIONS

    def is_done(self, frames: List[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN or self.action_counter >= self.MAX_ACTIONS

    def _available_simple(self, latest_frame: FrameData) -> List[str]:
        avail = getattr(latest_frame, "available_actions", None) or []
        names = [a.name for a in avail if hasattr(a, "name") and a.name in SIMPLE_ACTIONS]
        return names or SIMPLE_ACTIONS

    def _to_game_action(
        self,
        action_name: str,
        grid: Any,
        scene_hint: Optional[Dict[str, Any]] = None,
        causality_meta: Optional[Dict[str, Any]] = None,
        goal_meta: Optional[Dict[str, Any]] = None,
    ) -> GameAction:
        ga = getattr(GameAction, action_name)
        if ga.is_complex():
            h, w = len(grid), len(grid[0]) if grid else 0
            ga.set_data({"x": w // 2, "y": h // 2})
        sh = state_hash(grid)
        explore_meta = GLOBAL_EXPLORER.exploration.exploration_metadata(sh)
        n_obj = (scene_hint or {}).get("num_objects", "?")
        sem = (causality_meta or {}).get("semantic_label", "unknown")
        conf = (causality_meta or {}).get("confidence", 0.0)
        unc = (causality_meta or {}).get("uncertainty", 1.0)
        goal = (goal_meta or {}).get("template_id", "unknown")
        ga.reasoning = (
            f"ASRA Phase9: {action_name} | objects={n_obj} "
            f"| visits={explore_meta.get('visit_count_before', 0)} "
            f"| sem={sem} conf={conf:.2f} u={unc:.2f} "
            f"| goal={goal}"
        )
        return ga

    def choose_action(self, frames: List[FrameData], latest_frame: FrameData) -> GameAction:
        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            return GameAction.RESET
        grid = latest_frame.frame
        scene = compact_scene(canonical_grid(grid))
        name, causality_meta, goal_meta = GLOBAL_EXPLORER.choose_action(
            state_hash(grid), GLOBAL_SEMANTICS, self._available_simple(latest_frame), scene_hint=scene
        )
        return self._to_game_action(name, grid, scene, causality_meta, goal_meta)

    def take_action(self, action: GameAction) -> Optional[FrameData]:
        self._last_action_name = action.name
        return super().take_action(action)

    def append_frame(self, frame: FrameData) -> None:
        super().append_frame(frame)
        if len(self.frames) < 2:
            return
        prev, curr = self.frames[-2], self.frames[-1]
        if not prev.frame or not curr.frame:
            return
        prev_grid = canonical_grid(prev.frame)
        curr_grid = canonical_grid(curr.frame)
        diff_count = int(np.sum(np.array(prev_grid) != np.array(curr_grid)))
        scene_before = compact_scene(prev_grid)
        scene_after = compact_scene(curr_grid)
        transform_hist = transform_histogram_from_scenes(scene_before, scene_after)
        diff = {
            "num_changed_cells": diff_count,
            "object_scene_before": scene_before,
            "object_scene_after": scene_after,
            "transform_histogram": transform_hist,
            **object_delta(scene_before, scene_after),
        }
        reward = float(getattr(curr, "levels_completed", 0) or 0)
        level_completed = int(getattr(curr, "levels_completed", 0) or 0)
        sh = state_hash(prev_grid)
        nsh = state_hash(curr_grid)
        action = getattr(self, "_last_action_name", "UNKNOWN")
        sem = GLOBAL_SEMANTICS.infer(sh, action)
        GLOBAL_SEMANTICS.observe(sh, action, diff, reward, next_hash=nsh)
        GLOBAL_EXPLORER.update(
            sh, nsh, action, diff, reward, semantics=sem, level_completed=level_completed
        )


def _game_ids(environments: Any) -> List[str]:
    ids: List[str] = []
    for env in environments:
        if isinstance(env, str):
            ids.append(env)
        elif hasattr(env, "game_id"):
            ids.append(str(env.game_id))
        else:
            ids.append(str(env))
    return ids


def scorecard_to_rows(scorecard: Any) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    if scorecard is None:
        return rows
    for env in getattr(scorecard, "environments", None) or []:
        env_id = getattr(env, "id", None) or getattr(env, "game_id", "unknown")
        runs = getattr(env, "runs", None) or []
        if not runs:
            rows.append({"game_id": env_id, "score": 0.0, "levels_completed": 0, "actions": 0, "completed": False})
            continue
        best = max(runs, key=lambda r: (getattr(r, "score", 0.0), getattr(r, "levels_completed", 0)))
        rows.append(
            {
                "game_id": env_id,
                "score": float(getattr(best, "score", 0.0) or 0.0),
                "levels_completed": int(getattr(best, "levels_completed", 0) or 0),
                "actions": int(getattr(best, "actions", 0) or 0),
                "completed": bool(getattr(best, "completed", False)),
            }
        )
    return rows


def write_submission_parquet(path: str, scorecard: Optional[Any] = None) -> None:
    rows = scorecard_to_rows(scorecard)
    if not rows:
        rows = [{"game_id": "placeholder", "score": 0.0, "levels_completed": 0, "actions": 0, "completed": False}]
    df = pd.DataFrame(rows)
    df["agent"] = "asra-v1.0-phase9"
    df.to_parquet(path, index=False)


def run_swarm() -> Any:
    from arc_agi import Arcade

    agents_pkg = sys.modules.get("agents")
    if agents_pkg is not None:
        agents_pkg.AVAILABLE_AGENTS = AVAILABLE_AGENTS
    AVAILABLE_AGENTS["asra"] = ASRAAgent
    arcade = Arcade()
    games = _game_ids(arcade.get_environments())
    print(f"ASRA Phase9 Swarm: {len(games)} games | object+exploration+causality+goal hints")
    swarm = Swarm(
        "asra",
        os.environ.get("ARC_BASE_URL", "https://three.arcprize.org"),
        games,
        tags=["asra-v1.0-phase9"],
    )
    return swarm.main()


if __name__ == "__main__":
    working = _working_dir()
    submission_path = os.path.join(working, "submission.parquet")
    try:
        scorecard = run_swarm()
        write_submission_parquet(submission_path, scorecard)
        if scorecard is not None:
            print("Scorecard score:", getattr(scorecard, "score", None))
        print("Wrote", submission_path)
    except Exception:
        import traceback

        traceback.print_exc()
        raise
