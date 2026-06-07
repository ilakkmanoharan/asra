# Phase 5 — Implementation Reference

**Status:** **COMPLETE** — library `asra-arc/src/asra/goals/` + Kaggle v0.7-phase5  
**Agent tag:** `asra-v0.7-phase5`  
**Spec:** [`phase5-goal-inference-hypothesis-engine.md`](phase5-goal-inference-hypothesis-engine.md)

---

## Planned library modules (`asra-arc/src/asra/goals/`)

| Module | Role |
|--------|------|
| `schemas.py` | `GoalHypothesis`, `ProgressSignal`, `ObjectRole`, `ExperimentPlan` |
| `goal_hypothesis_generator.py` | Spawn templates from scene + ARC priors |
| `progress_detector.py` | reward, level_up, object/pattern progress |
| `object_role_classifier.py` | agent, target, token, hazard, key, door |
| `win_condition_inference.py` | WIN / near-WIN retrospective scoring |
| `hypothesis_ranker.py` | score, rank, confirm/refute lifecycle |
| `experiment_planner.py` | top-2 discrimination × Phase 4 uncertainty |
| `goals_store.py` | Online ingest + persistent hypotheses JSON |
| `arc_goals.py` | Batch mine JSONL + Original ARC pairs |
| `phyre_goals.py` | PHYRE success-template eval |
| `clevr_goals.py` | CLEVR role + relational goal probes |
| `policy_v4.py` | `GoalHypothesisExplorationPolicyV4` extends Phase 4 v3 |

---

## Planned CLI

```bash
cd asra-arc
PYTHONPATH=src python3 -m asra build-goal-hypotheses \
  --transitions-dir data/transitions \
  --arc-tasks-dir data/arc/original \
  --output-dir data/goals/arc

PYTHONPATH=src python3 -m asra eval-phase5-arc \
  --hypotheses-dir data/goals/arc/hypotheses \
  --output data/analysis/phase5/arc_goals_eval.json
```

Scripts (planned):

```bash
PYTHONPATH=src python3 scripts/build_goal_hypotheses.py
PYTHONPATH=src python3 scripts/eval_phase5_arc_goals.py
```

---

## Kaggle package (`private/phase5/`)

| File | Role |
|------|------|
| `asra_phase5_my_agent.py` | Competition agent — embedded `GoalHypothesisEngine` + Phase 4 `CausalSemanticsEngine` |
| `asra-phase-5-arc-prize-2026.ipynb` | Submit notebook |
| `build_phase5_kaggle_notebook.py` | Regenerate notebook from agent |
| `kernel-metadata.json` | Kaggle kernel metadata |
| `push_and_submit.py` / `submit.sh` | Push + submit helpers |

**Build notebook from agent:**

```bash
cd private/phase5
python3 build_phase5_kaggle_notebook.py
```

**Local self-test (no ARC runtime):**

```bash
python3 asra_phase5_my_agent.py --self-test
```

**Submit to Kaggle:**

```bash
cd private/phase5
./submit.sh all "ASRA v0.7-phase5 goal inference"
```

---

## Embedded Kaggle components (implemented)

### `GoalHypothesisEngine`

- Template library: `move_to_target`, `match_pattern`, `collect_tokens`, `avoid_hazard`, `unlock_passage`, `transform_to_goal`
- `ensure_hypotheses(scene)` — spawn once per episode
- `observe_progress(reward, level_delta, semantics, diff)` — update support/refute/progress_score
- `rank_hypotheses()` / `leading_hypothesis()`
- `action_goal_score(semantics)` — alignment with leading template operators
- `experiment_discrimination_bonus(state, action, semantics_engine)` — top-2 separation × uncertainty

### Policy integration

```text
score(action) = Phase1–4 terms
              + GOAL_HINT_WEIGHT · action_goal_score
              + EXPERIMENT_HINT_WEIGHT · discrimination_bonus
```

Env overrides: `ASRA_GOAL_HINT_WEIGHT`, `ASRA_EXPERIMENT_HINT_WEIGHT`

---

## Transition metadata (Phase 5 — planned online)

When using `GoalsStore.ingest_transition`:

```json
"metadata": {
  "goals": {
    "leading_hypothesis_id": "gh_3_move_to_target",
    "leading_template_id": "move_to_target",
    "progress_score": 4.2,
    "object_roles": {"obj_0": "agent", "obj_1": "target"},
    "experiment_plan_id": "exp_12"
  }
}
```

---

## Data paths (planned)

```text
asra-arc/data/goals/arc/
  hypotheses/
  progress_events/
  object_roles/
asra-arc/data/analysis/phase5/
```

---

## Milestone status

| Milestone | Status |
|-----------|--------|
| **5A** Spec + schemas | done — `private/phase5/phase5-goal-inference-hypothesis-engine.md` |
| **5B** Theory article | done — `asra-phase5-goal-inference-hypothesis-engine.md` |
| **5C** Kaggle agent + notebook | done — `asra_phase5_my_agent.py`, notebook, self-test PASS |
| **5D** Library `goals/` package | planned |
| **5E** Original ARC + PHYRE/CLEVR eval | planned |
| **5F** Competition submit | pending — push kernel when ready |

---

## Tests (planned)

```bash
cd asra-arc && PYTHONPATH=src python3 -m pytest tests/test_goals.py -q
```

Kaggle embedded self-test (today):

```bash
python3 private/phase5/asra_phase5_my_agent.py --self-test
# perception + exploration + causality + goals OK
```
