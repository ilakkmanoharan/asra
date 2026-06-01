"""ASRA Phase 2 agent for ARC Prize 2026 — ARC-AGI-3 (Kaggle Swarm).

Includes compact object-scene hints (Phase 2 perception) in transition logging and exploration bias.
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
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Tuple

# --- compact object perception (embedded; mirrors asra_phase2_compact_perception.py) ---


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
        cy = sum(ys) / n
        cx = sum(xs) / n
        objects.append(
            {"object_id": f"obj_{idx}", "color": int(color), "area": n, "bbox": bbox, "centroid": [cy, cx]}
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


# --- Kaggle bootstrap (venv re-exec; matches Phase 1 v4-fixed notebook) ---


def _working_dir() -> str:
    return "/kaggle/working" if os.path.isdir("/kaggle/working") else "."


def _venv_dir(working: str) -> str:
    # Keep venv off /kaggle/working — site-packages floods saved outputs (500 file cap).
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
        raise RuntimeError(
            f"ARC-AGI-3 runtime not ready. comp_root={comp_root!r} agents_root={agents_root!r}"
        )
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
    grid2 = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    delta = object_delta(scene, compact_scene(grid2))
    assert delta["delta_num_objects"] <= 0
    print(f"compact_scene objects={scene['num_objects']}")
    print("perception self-test OK")


AGENTS_ROOT = _bootstrap_kaggle()

import numpy as np
import pandas as pd
from arcengine import FrameData, GameAction, GameState

Agent, Swarm, AVAILABLE_AGENTS = _load_agents_runtime(AGENTS_ROOT)

SEED = int(os.environ.get("ASRA_SEED", "42"))
MAX_ACTIONS = int(os.environ.get("ASRA_MAX_ACTIONS", "80"))
SIMPLE_ACTIONS = ["ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5", "ACTION7"]
OBJECT_HINT_WEIGHT = float(os.environ.get("ASRA_OBJECT_HINT_WEIGHT", "0.35"))

random.seed(SEED)
np.random.seed(SEED)


def canonical_grid(grid: Any) -> List[List[int]]:
    return np.array(grid, dtype=int).tolist()


def state_hash(grid: Any) -> str:
    payload = json.dumps(canonical_grid(grid), separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class ActionSemanticsInferencer:
    def __init__(self) -> None:
        self.effects: Dict[Tuple[str, str], List[Dict[str, Any]]] = defaultdict(list)

    def observe(self, state_hash_value: str, action: str, diff: Dict[str, Any], reward: float) -> None:
        self.effects[(state_hash_value, action)].append(
            {
                "num_changed_cells": diff.get("num_changed_cells"),
                "reward": reward,
                "delta_num_objects": diff.get("delta_num_objects"),
            }
        )

    def infer(self, state_hash_value: str, action: str) -> Dict[str, Any]:
        effects = self.effects.get((state_hash_value, action), [])
        if not effects:
            return {"observations": 0, "hypothesis": "unknown", "consistency_score": None}
        counts = [e["num_changed_cells"] for e in effects if e["num_changed_cells"] is not None]
        obj_deltas = [e.get("delta_num_objects") for e in effects if e.get("delta_num_objects") is not None]
        std = float(np.std(counts)) if counts else 0.0
        mean = float(np.mean(counts)) if counts else None
        if mean == 0:
            hyp = "no-op / blocked"
        elif mean is not None and mean <= 1.5:
            hyp = "localized cell update"
        else:
            hyp = "multi-cell transform"
        obj_mean = float(np.mean(obj_deltas)) if obj_deltas else 0.0
        return {
            "observations": len(effects),
            "hypothesis": hyp,
            "consistency_score": float(1.0 / (1.0 + std)) if counts else None,
            "mean_delta_objects": obj_mean,
        }


class ASRAExplorer:
    def __init__(self, action_names: List[str]) -> None:
        self.action_names = action_names
        self.state_action_counts: Counter = Counter()
        self.action_rewards: Dict[str, List[float]] = defaultdict(list)
        self.object_effect_scores: Dict[Tuple[str, str], float] = defaultdict(float)
        self.dead_ends: set = set()

    def update(self, state_hash_value: str, action: str, diff: Dict[str, Any], reward: float) -> None:
        self.state_action_counts[(state_hash_value, action)] += 1
        self.action_rewards[action].append(float(reward))
        if diff.get("num_changed_cells") == 0 and reward <= 0:
            self.dead_ends.add((state_hash_value, action))
        delta_obj = diff.get("delta_num_objects")
        if delta_obj is not None and delta_obj != 0:
            key = (state_hash_value, action)
            self.object_effect_scores[key] += 0.5 * (1.0 if delta_obj > 0 else 0.7)

    def choose_action(
        self,
        state_hash_value: str,
        semantics: ActionSemanticsInferencer,
        available: Optional[List[str]] = None,
        scene_hint: Optional[Dict[str, Any]] = None,
    ) -> str:
        candidates = [a for a in self.action_names if available is None or a in available] or list(self.action_names)
        scores: Dict[str, float] = {}
        num_objects = int((scene_hint or {}).get("num_objects", 0))
        for action in candidates:
            if (state_hash_value, action) in self.dead_ends:
                continue
            sem = semantics.infer(state_hash_value, action)
            c = sem.get("consistency_score")
            uncertainty = 1.0 if c is None else (1.0 - min(1.0, c))
            local = self.state_action_counts[(state_hash_value, action)]
            mean_r = float(np.mean(self.action_rewards[action])) if self.action_rewards[action] else 0.0
            obj_bonus = OBJECT_HINT_WEIGHT * self.object_effect_scores.get((state_hash_value, action), 0.0)
            if num_objects == 0:
                obj_bonus *= 0.5
            scores[action] = (
                2.0 / (1.0 + local) + 0.7 * uncertainty + 0.5 * mean_r + obj_bonus + random.random() * 0.05
            )
        return max(scores.items(), key=lambda kv: kv[1])[0] if scores else random.choice(candidates)


GLOBAL_SEMANTICS = ActionSemanticsInferencer()
GLOBAL_EXPLORER = ASRAExplorer(SIMPLE_ACTIONS)


class ASRAAgent(Agent):
    """Phase 2: transition logging + compact object-scene hints for exploration."""

    MAX_ACTIONS = MAX_ACTIONS

    def is_done(self, frames: List[FrameData], latest_frame: FrameData) -> bool:
        return latest_frame.state is GameState.WIN or self.action_counter >= self.MAX_ACTIONS

    def _available_simple(self, latest_frame: FrameData) -> List[str]:
        avail = getattr(latest_frame, "available_actions", None) or []
        names = [a.name for a in avail if hasattr(a, "name") and a.name in SIMPLE_ACTIONS]
        return names or SIMPLE_ACTIONS

    def _to_game_action(self, action_name: str, grid: Any, scene_hint: Optional[Dict[str, Any]] = None) -> GameAction:
        ga = getattr(GameAction, action_name)
        if ga.is_complex():
            h, w = len(grid), len(grid[0]) if grid else 0
            ga.set_data({"x": w // 2, "y": h // 2})
        n_obj = (scene_hint or {}).get("num_objects", "?")
        ga.reasoning = f"ASRA Phase2: {action_name} | objects={n_obj}"
        return ga

    def choose_action(self, frames: List[FrameData], latest_frame: FrameData) -> GameAction:
        if latest_frame.state in (GameState.NOT_PLAYED, GameState.GAME_OVER):
            return GameAction.RESET
        grid = latest_frame.frame
        scene = compact_scene(canonical_grid(grid))
        name = GLOBAL_EXPLORER.choose_action(
            state_hash(grid), GLOBAL_SEMANTICS, self._available_simple(latest_frame), scene_hint=scene
        )
        return self._to_game_action(name, grid, scene)

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
        diff = {
            "num_changed_cells": diff_count,
            "object_scene_before": scene_before,
            "object_scene_after": scene_after,
            **object_delta(scene_before, scene_after),
        }
        reward = float(getattr(curr, "levels_completed", 0) or 0)
        sh = state_hash(prev_grid)
        action = getattr(self, "_last_action_name", "UNKNOWN")
        GLOBAL_SEMANTICS.observe(sh, action, diff, reward)
        GLOBAL_EXPLORER.update(sh, action, diff, reward)


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
    df["agent"] = "asra-v0.4-phase2"
    df.to_parquet(path, index=False)


def run_swarm() -> Any:
    from arc_agi import Arcade

    agents_pkg = sys.modules.get("agents")
    if agents_pkg is not None:
        agents_pkg.AVAILABLE_AGENTS = AVAILABLE_AGENTS
    AVAILABLE_AGENTS["asra"] = ASRAAgent
    arcade = Arcade()
    games = _game_ids(arcade.get_environments())
    print(f"ASRA Phase2 Swarm: {len(games)} games | object_hints=on")
    swarm = Swarm(
        "asra",
        os.environ.get("ARC_BASE_URL", "https://three.arcprize.org"),
        games,
        tags=["asra-v0.4-phase2"],
    )
    return swarm.main()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        perception_self_test()
        assert hasattr(ASRAAgent, "choose_action")
        print(f"python={sys.executable}")
        print("runtime self-test OK (Phase 2)")
        sys.exit(0)

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
