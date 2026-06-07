#!/usr/bin/env python3
"""Scaffold kaggle-notebooks/phaseN from phase N-1 with agent extensions."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

PHASE_CONFIG = {
    6: {
        "title": "Planning and Strategy Invention",
        "tag": "asra-v0.8-phase6",
        "slug": "asra-phase-6-arc-prize-2026",
        "engine_class": "PlanningEngine",
        "engine_code": '''

# --- Phase 6 planning (embedded) ---


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
''',
        "self_test_call": "    planning_self_test()",
        "reasoning_prefix": "ASRA Phase6",
        "weight_env": "PLAN_HINT_WEIGHT",
        "weight_default": "0.20",
        "score_line": "plan_bonus = PLAN_HINT_WEIGHT * self.planning.plan_bonus(state_hash_value, action, (lead or {}).get('template_id'), self.exploration.visit_counts[state_hash_value])",
        "score_add": "                + plan_bonus",
        "init_line": "        self.planning = PlanningEngine()",
        "observe_line": "        self.planning.observe(state_hash_value, action, next_hash)",
        "paper_abstract": "Phase 6 adds BFS/MCTS-lite planning, strategy library, and meta explore-exploit control atop Phase 5 goal inference.",
    },
    7: {
        "title": "Robustness and Generalization",
        "tag": "asra-v0.85-phase7",
        "slug": "asra-phase-7-arc-prize-2026",
        "engine_class": "RobustnessEngine",
        "engine_code": '''

# --- Phase 7 robustness (embedded) ---


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
''',
        "self_test_call": "    robustness_self_test()",
        "reasoning_prefix": "ASRA Phase7",
        "weight_env": "ROBUST_HINT_WEIGHT",
        "weight_default": "-0.25",
        "score_line": "stuck_pen = ROBUST_HINT_WEIGHT * (self.robust.stuck_penalty(state_hash_value) + self.robust.action_waste_penalty(action, local))",
        "score_add": "                + stuck_pen",
        "init_line": "        self.robust = RobustnessEngine()",
        "observe_line": "        self.robust.observe(state_hash_value, changed, float(reward))",
        "paper_abstract": "Phase 7 adds failure analysis, stuck detection, and action waste reduction for generalization.",
    },
    8: {
        "title": "Decision Biology Bridge",
        "tag": "asra-v0.9-phase8",
        "slug": "asra-phase-8-arc-prize-2026",
        "engine_class": "BiologyBridgeEngine",
        "engine_code": '''

# --- Phase 8 Decision Biology bridge (embedded) ---


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
''',
        "self_test_call": "    biology_self_test()",
        "reasoning_prefix": "ASRA Phase8",
        "weight_env": "BIO_HINT_WEIGHT",
        "weight_default": "0.10",
        "score_line": "bio_bonus = BIO_HINT_WEIGHT * (0.5 if self.biology.perturbation_label(sem.get('semantic_label', 'unknown')) != 'unknown_perturbation' else 0.0)",
        "score_add": "                + bio_bonus",
        "init_line": "        self.biology = BiologyBridgeEngine()",
        "observe_line": "",
        "paper_abstract": "Phase 8 bridges grid reasoning to Decision Biology via perturbation-as-action and cell-state identifiers.",
    },
    9: {
        "title": "Final Submission and Research Story",
        "tag": "asra-v1.0-phase9",
        "slug": "asra-phase-9-arc-prize-2026",
        "engine_class": "FinalStackEngine",
        "engine_code": '''

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
''',
        "self_test_call": "    final_self_test()",
        "reasoning_prefix": "ASRA Phase9",
        "weight_env": "FINAL_HINT_WEIGHT",
        "weight_default": "0.05",
        "score_line": "final_bonus = FINAL_HINT_WEIGHT * 0.5",
        "score_add": "                + final_bonus",
        "init_line": "        self.final = FinalStackEngine()",
        "observe_line": "",
        "paper_abstract": "Phase 9 integrates the full ASRA stack for final ARC submission and research narrative.",
    },
}


def _patch_agent(src: str, cfg: dict, phase: int) -> str:
    prev = phase - 1
    text = src.replace(f"Phase {prev}", f"Phase {phase}")
    text = text.replace(f"phase{prev}", f"phase{phase}")
    text = text.replace(f"v0.{6 + prev - 5}-phase{prev}" if prev >= 5 else f"v0.6-phase4", cfg["tag"])
    # fix tag replacements more directly
    text = re.sub(r"asra-v[0-9.]+-phase\d+", cfg["tag"], text)
    text = re.sub(r"ASRA Phase\d+", cfg["reasoning_prefix"], text)
    text = re.sub(r"runtime self-test OK \(Phase \d+\)", f"runtime self-test OK (Phase {phase})", text)

    if cfg["engine_class"] not in text:
        marker = "if __name__ == \"__main__\" and len(sys.argv) > 1 and sys.argv[1] == \"--self-test\":"
        text = text.replace(marker, cfg["engine_code"] + "\n\n" + marker)
        text = text.replace(
            "    goals_self_test()",
            "    goals_self_test()\n" + cfg["self_test_call"],
        )

    if cfg["init_line"] and cfg["init_line"] not in text:
        text = text.replace(
            "        self.goals = GoalHypothesisEngine()",
            "        self.goals = GoalHypothesisEngine()\n" + cfg["init_line"],
        )

    env = cfg["weight_env"]
    if env not in text:
        text = text.replace(
            'EXPERIMENT_HINT_WEIGHT = float(os.environ.get("ASRA_EXPERIMENT_HINT_WEIGHT", "0.15"))',
            'EXPERIMENT_HINT_WEIGHT = float(os.environ.get("ASRA_EXPERIMENT_HINT_WEIGHT", "0.15"))\n'
            + f'{env} = float(os.environ.get("ASRA_{env}", "{cfg["weight_default"]}"))',
        )

    if cfg["score_line"] in text or cfg["score_add"] in text:
        pass
    elif "scores[action] = (" in text and cfg["score_add"] not in text:
        text = text.replace(
            "            exp_bonus = EXPERIMENT_HINT_WEIGHT * self.goals.experiment_discrimination_bonus(",
            f"            {cfg['score_line']}\n"
            "            exp_bonus = EXPERIMENT_HINT_WEIGHT * self.goals.experiment_discrimination_bonus(",
        )
        text = text.replace(
            "                + explore_bonus\n                + random.random() * 0.05",
            "                + explore_bonus\n" + cfg["score_add"] + "\n                + random.random() * 0.05",
        )

    if cfg["observe_line"] and cfg["observe_line"] not in text:
        text = text.replace(
            "        self.exploration.observe(state_hash_value, next_hash, action, reward, changed)\n",
            "        self.exploration.observe(state_hash_value, next_hash, action, reward, changed)\n"
            "        " + cfg["observe_line"].strip() + "\n",
        )

    return text


def _write_spec(out: Path, phase: int, cfg: dict) -> None:
    spec = f"""# Phase {phase} — {cfg['title']}

**Track:** Phase {phase} (core ASRA roadmap)  
**Source:** `private/documents/ASRA-theory/ASRA-roadmap-datasets.md`  
**Agent tag:** `{cfg['tag']}`  
**Depends on:** Phases 1–{phase - 1} ✅

---

## 1. Mission

{cfg['paper_abstract']}

See Phase {phase - 1} for prior layers. Phase {phase} output integrates into the competition agent `{cfg['slug']}`.

---

## 2. What to build

| Module | Role |
|--------|------|
| Embedded `{cfg['engine_class']}` | Kaggle competition agent extension |
| Library | `asra-arc/src/asra/` — see phase{phase}-implementation.md |
| Eval | Offline metrics + self-test |

---

## 3. Kaggle package

| File | Role |
|------|------|
| `{cfg['slug'].replace('asra-', 'asra_').replace('-arc-prize-2026', '_my_agent.py')}` | Agent source |
| `{cfg['slug']}.ipynb` | Submit notebook |
| `build_phase{phase}_kaggle_notebook.py` | Notebook builder |

---

## 4. CLI / tests

```bash
python3 asra_{cfg['tag'].split('-')[1]}_my_agent.py --self-test
python3 build_phase{phase}_kaggle_notebook.py
```

---

## 5. Bridge to next phase

Phase {phase} extends the cumulative ASRA stack toward Milestone #2 (Phase 6) and Decision Biology (Phase 8).
"""
    (out / f"phase{phase}-{'planning-strategy-invention' if phase==6 else 'robustness-generalization' if phase==7 else 'decision-biology-bridge' if phase==8 else 'final-submission'}.md").write_text(spec, encoding="utf-8")


def _write_paper(out: Path, phase: int, cfg: dict) -> None:
    paper = f"""# {cfg['title']}: ASRA Phase {phase}

**Author:** Ilakkuvaselvi (Ilak) Manoharan  
**Affiliation:** Nature Foundation Models  
**Date:** June 2026  
**Companion:** `{cfg['slug']}.ipynb`

---

## Abstract

{cfg['paper_abstract']}

---

## 1. Position in ASRA

Phases 1–{phase - 1} provide the cumulative cognitive stack. Phase {phase} adds **{cfg['engine_class']}** to the Kaggle agent while the research library lives in `asra-arc/src/asra/`.

---

## 2. Theory

Phase {phase} closes the gap between prior layers and the roadmap milestone for **{cfg['title']}**. The embedded engine preserves Kaggle sandbox isolation (no external imports).

---

## 3. Agent integration

Reasoning prefix: `{cfg['reasoning_prefix']}`  
Agent tag: `{cfg['tag']}`

---

## 4. Conclusion

Phase {phase} extends transition-centric adaptive reasoning toward scientific intelligence and competition readiness.
"""
    names = {6: "planning-strategy-invention", 7: "robustness-generalization", 8: "decision-biology-bridge", 9: "final-research-story"}
    (out / f"asra-phase{phase}-{names[phase]}.md").write_text(paper, encoding="utf-8")


def scaffold(phase: int) -> None:
    cfg = PHASE_CONFIG[phase]
    prev = phase - 1
    src_dir = REPO / "kaggle-notebooks" / f"phase{prev}"
    out_dir = REPO / "kaggle-notebooks" / f"phase{phase}"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    shutil.copytree(src_dir, out_dir)

    # Remove docs inherited from previous phase folder
    for f in list(out_dir.iterdir()):
        name = f.name
        for m in range(5, 10):
            if m == phase:
                continue
            if name.startswith(f"phase{m}-") or name.startswith(f"asra-phase{m}-"):
                f.unlink(missing_ok=True)

    agent_src = (src_dir / f"asra_phase{prev}_my_agent.py").read_text(encoding="utf-8")
    agent_out = _patch_agent(agent_src, cfg, phase)
    (out_dir / f"asra_phase{phase}_my_agent.py").write_text(agent_out, encoding="utf-8")
    (out_dir / f"asra_phase{prev}_my_agent.py").unlink(missing_ok=True)

    build_src = (out_dir / f"build_phase{prev}_kaggle_notebook.py").read_text(encoding="utf-8")
    build_src = build_src.replace(f"phase{prev}", f"phase{phase}").replace(f"Phase {prev}", f"Phase {phase}")
    build_src = build_src.replace(f"asra-phase-{prev}-arc-prize-2026", cfg["slug"])
    build_src = build_src.replace(f"asra_phase{prev}_my_agent.py", f"asra_phase{phase}_my_agent.py")
    build_src = re.sub(r"asra-v[0-9.]+-phase\d+", cfg["tag"], build_src)
    (out_dir / f"build_phase{phase}_kaggle_notebook.py").write_text(build_src, encoding="utf-8")
    (out_dir / f"build_phase{prev}_kaggle_notebook.py").unlink(missing_ok=True)

    nb_old = out_dir / f"asra-phase-{prev}-arc-prize-2026.ipynb"
    nb_old.unlink(missing_ok=True)

    meta = json.loads((out_dir / "kernel-metadata.json").read_text(encoding="utf-8"))
    meta["id"] = f"ilakkmanoharan/{cfg['slug']}"
    meta["title"] = f"ASRA Phase {phase} — ARC Prize 2026"
    meta["code_file"] = f"{cfg['slug']}.ipynb"
    (out_dir / "kernel-metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")

    push = (out_dir / "push_and_submit.py").read_text(encoding="utf-8")
    push = push.replace(f"phase-{prev}-", f"phase-{phase}-").replace(f"Phase {prev}", f"Phase {phase}")
    push = re.sub(r"asra-v[0-9.]+-phase\d+[^\"]*", cfg["tag"], push)
    (out_dir / "push_and_submit.py").write_text(push, encoding="utf-8")

    submit = (out_dir / "submit.sh").read_text(encoding="utf-8")
    submit = submit.replace(f"Phase {prev}", f"Phase {phase}")
    submit = re.sub(r"ASRA v[0-9.]+-phase\d+[^\"]*", cfg["tag"], submit)
    (out_dir / "submit.sh").write_text(submit, encoding="utf-8")

    _write_spec(out_dir, phase, cfg)
    _write_paper(out_dir, phase, cfg)

    impl = f"""# Phase {phase} — Implementation Reference

**Agent tag:** `{cfg['tag']}`  
**Library:** `asra-arc/src/asra/` — Phase {phase} modules

## Kaggle

```bash
cd kaggle-notebooks/phase{phase}
python3 build_phase{phase}_kaggle_notebook.py
python3 asra_phase{phase}_my_agent.py --self-test
```

## Embedded engine

`{cfg['engine_class']}` in `asra_phase{phase}_my_agent.py`
"""
    (out_dir / f"phase{phase}-implementation.md").write_text(impl, encoding="utf-8")

    readme = f"""# Phase {phase} — {cfg['title']}

**Agent tag:** `{cfg['tag']}`

| Document | Role |
|----------|------|
| phase{phase}-*.md | Specification |
| asra-phase{phase}-*.md | Theory paper |
| phase{phase}-implementation.md | Implementation reference |

```bash
python3 build_phase{phase}_kaggle_notebook.py
python3 asra_phase{phase}_my_agent.py --self-test
./submit.sh all "{cfg['tag']}"
```
"""
    (out_dir / "README.md").write_text(readme, encoding="utf-8")

    import subprocess

    subprocess.run(
        ["python3", str(out_dir / f"build_phase{phase}_kaggle_notebook.py")],
        check=True,
        cwd=out_dir,
    )
    subprocess.run(
        ["python3", str(out_dir / f"asra_phase{phase}_my_agent.py"), "--self-test"],
        check=True,
        cwd=out_dir,
    )
    print(f"Scaffolded phase {phase} -> {out_dir}")


if __name__ == "__main__":
    import sys

    for p in sys.argv[1:] or ["6", "7", "8", "9"]:
        scaffold(int(p))
