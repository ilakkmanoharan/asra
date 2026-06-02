# ASRA Phase 3 — Implementation Reference

**Status:** COMPLETE (Milestones 3A–3D)  
**Agent tag:** `asra-v0.5-phase3`  
**Policy name:** `exploration_v2`  
**Library path:** `asra-arc/src/asra/exploration/`  
**Last updated:** June 2026  
**Author:** Ilakkuvaselvi (Ilak) Manoharan

> **Theory & roadmap:** [phase3-exploration-memory-navigation.md](phase3-exploration-memory-navigation.md)  
> **Quick index:** [README.md](README.md)

This document records **what was built**, **where it lives**, and **how to run it** — the implementation companion to the Phase 3 specification.

---

## 1. Summary

Phase 3 delivers the **Navigation & Memory Engine**: an exploration-centric layer on top of Phase 1 transitions and Phase 2 object scenes. The agent remembers visited states, scores actions by novelty and usefulness, tracks subgoals, reuses successful action sequences, and replays high-value transitions.

| Milestone | Focus | Status |
|-----------|--------|--------|
| **3A** | MiniGrid foundation — graph, memory, novelty, policy, runner | ✅ |
| **3B** | Useful exploration — DoorKey eval, replay export, baseline comparison | ✅ |
| **3C** | BabyAI subgoals — mission parser, detector, eval harness | ✅ |
| **3D** | ARC-AGI-3 integration — dual-key novelty, ablation, Kaggle hints | ✅ |

**Verification:** 60/60 tests pass in `asra-arc` (`pytest tests/test_exploration_*.py` and related).

---

## 2. Architecture

```text
                    ┌─────────────────────────────────────┐
                    │         Environment adapters         │
                    │  MiniGrid │ BabyAI │ ARC-AGI-3      │
                    └─────────────────┬───────────────────┘
                                      │ frames, reward
                                      ▼
                    ┌─────────────────────────────────────┐
                    │   Phase 1 — EpisodeLogger / τ schema   │
                    └─────────────────┬───────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│ Phase 2 snapshot│       │ ExplorationGraph │       │ VisitationMemory│
│ (object scene)  │──────▶│ + frontiers      │◀──────│ hash + object fp│
└─────────────────┘       └────────┬─────────┘       └─────────────────┘
                                   │
                    ┌──────────────┼──────────────┐
                    ▼              ▼              ▼
              NoveltyScorer  UsefulnessScorer  SubgoalDetector
                    │              │              │
                    └──────────────┼──────────────┘
                                   ▼
                    ┌─────────────────────────────────────┐
                    │      ExplorationPolicyV2             │
                    │  (or Phase1PolicyAdapter baseline)   │
                    └─────────────────┬───────────────────┘
                                      │
                    ┌─────────────────┴─────────────────┐
                    ▼                                   ▼
           TransitionReplayBuffer              StrategyLibrary
```

**Cross-episode state:** `ExplorationSessionState` holds shared `VisitationMemory`, `ExplorationGraph`, `StrategyLibrary`, and `TransitionReplayBuffer` across batch runs so strategies learned in episode *n* bias episode *n+1*.

---

## 3. Package layout

```text
asra-arc/
  src/asra/exploration/
    __init__.py              # Public exports
    schemas.py               # ExplorationNode, ExplorationEdge, SubgoalState, StrategyPattern
    exploration_graph.py     # Frontier-aware graph; batch ingest from JSONL
    visitation_memory.py     # Visit counts, object fingerprints, recent window
    novelty.py               # State/edge novelty (dual-key with object scenes)
    usefulness.py            # Reward, frontier, subgoal, dead-end scoring
    policy_v2.py             # ExplorationPolicyV2 action selection
    policy_adapter.py        # Phase1PolicyAdapter (baseline for benchmarks)
    replay.py                # Priority replay buffer + JSONL export
    strategies.py            # StrategyLibrary — extract, match, bias
    subgoals.py              # Mission parser, SubgoalDetector, DoorKey milestones
    env_utils.py             # MiniGrid grid encoding, preconditions, action labels
    session.py               # ExplorationSessionState
    runner_core.py           # GymExplorationRunner (shared MiniGrid/BabyAI loop)
    minigrid_runner.py       # MiniGridRunner, batch + baseline batch
    babyai_runner.py         # BabyAIRunner, run_babyai_batch
    arc_exploration.py       # ArcExplorationRunner, per-episode graph build

  scripts/
    eval_phase3_minigrid.py
    eval_phase3_doorkey_benchmark.py
    eval_phase3_babyai.py
    eval_phase3_arc_ablation.py

kaggle-notebooks/
  asra_phase3_exploration_hints.py   # Compact Kaggle agent module
  phase3/
    README.md
    phase3-exploration-memory-navigation.md   # Spec
    phase3-implementation.md                    # This file
```

**Optional dependency:** `pip install -e '.[exploration]'` → `gymnasium>=0.29`, `minigrid>=2.3.0` (BabyAI envs ship inside minigrid; no separate `babyai` package required).

---

## 4. Core modules

### 4.1 Exploration graph (`exploration_graph.py`)

Extends Phase 1 hash-graph concepts with exploration metadata.

| Field (node) | Meaning |
|--------------|---------|
| `visit_count`, `first_seen_step`, `last_seen_step` | Temporal coverage |
| `frontier_score` | Fraction of successors with low visit count |
| `object_summary` | Phase 2 compact scene when attached |

| Field (edge) | Meaning |
|--------------|---------|
| `avg_novelty_gain`, `usefulness_score` | Rolling means from transition metadata |
| `dead_end` | Sticky flag for zero-progress edges |

**API:** `ExplorationGraph.add_transition()`, `frontier_score()`, `frontier_gain()`, `save()`, `build_exploration_graph_from_transitions(dir)`.

### 4.2 Visitation memory (`visitation_memory.py`)

| Layer | Key | Use |
|-------|-----|-----|
| Exact | `state_hash` | Revisit detection |
| Object | `object_scene_fingerprint` | Soft revisit (Phase 2 scenes) |
| Episodic | recent window (20) | Loop penalty in policy |

### 4.3 Novelty scorer (`novelty.py`)

```text
novelty(s) = 1 / sqrt(1 + visit_count(s))
           + α · 1[object_fingerprint unseen]
           + β · frontier_bonus(s)

edge_novelty = novelty(s′) + γ·reward − δ·dead_end
```

Defaults: `α=0.3`, `β=0.2`, `γ=0.1`, `δ=0.5`.

### 4.4 Usefulness scorer (`usefulness.py`)

Combines reward delta, frontier gain, subgoal progress, object-count delta, and dead-end penalty with configurable weights (`w_reward`, `w_frontier`, `w_subgoal`, `w_dead_end`, `w_object_delta`).

### 4.5 Exploration policy v2 (`policy_v2.py`)

Ranks actions by observed edge stats (avg novelty + usefulness − repeat penalty) or unexplored-edge prior (novelty + subgoal usefulness). Adds **strategy bias** (+0.4) when `StrategyLibrary` matches current precondition.

Returns: `{selected_action, reason, score, strategy_hint?}` where `reason ∈ {observed_edge, unexplored_edge, strategy_bias}`.

### 4.6 Phase 1 baseline adapter (`policy_adapter.py`)

`Phase1PolicyAdapter` wraps `SimpleExplorationPolicy` with the same `select_action(state_hash, actions, graph, memory, …)` interface for fair DoorKey benchmarks.

### 4.7 Strategy library (`strategies.py`)

| Capability | Description |
|------------|-------------|
| `add()` / `find_match()` | Precondition-keyed patterns |
| `bias_for_state()` | First action of best matching sequence |
| `extract_from_episode()` | Compress action list from WIN episodes |
| `save()` / `load()` | JSON persistence |
| `default_doorkey_strategy()` | Seed pattern for DoorKey cold start |

Precondition example: `{env_type: doorkey, has_key: false, door_open: false}`.

### 4.8 Subgoal detector (`subgoals.py`)

**BabyAI:** `parse_babyai_mission()` → subgoal list; `SubgoalDetector.from_mission(mission)`.

**DoorKey:** `SubgoalDetector.for_doorkey()` → `[has_key, door_open, at_goal]`.

**Oracle checks:**
- GoTo: agent `front_pos` matches target object position (BabyAI `GoToInstr`)
- Pickup / has_key: `carrying.type == key`
- door_open: any grid door cell `is_open`
- at_goal: `terminated` and `reward > 0`

### 4.9 Replay buffer (`replay.py`)

Max-heap priority buffer (capacity 500 default). Keeps **highest**-priority transitions. Priorities boosted for subgoal completions, WIN, high novelty/usefulness.

**Export:** `replay.export(path)` → JSONL of ranked transitions.

### 4.10 Environment utilities (`env_utils.py`)

- `encode_minigrid_grid(env)` — `Grid.encode()` + synthetic agent-pose row (position, direction, carry flag) so state hashes change when the agent moves
- `minigrid_precondition(env, env_id)` — tags for strategy matching
- `asra_action_names(n)` — `ACTION1`…`ACTION7` (Phase 1 schema compatible)
- `minigrid_action_label(idx)` — human-readable `left`, `forward`, etc. in metadata

---

## 5. Runners

### 5.1 Gym exploration runner (`runner_core.py`)

Shared loop for MiniGrid and BabyAI:

1. Reset env, log initial state
2. Each step: precondition → policy → env step → diff → transition
3. Attach `metadata.exploration` + env-specific fields
4. Update graph, memory, replay, policy observations
5. On WIN: extract strategy from episode

**Result type:** `GymEpisodeResult` — `episode_id`, `steps`, `success`, `unique_nodes`, `strategy_reused`, `subgoal_completions`, `transition_path`.

### 5.2 MiniGrid runner (`minigrid_runner.py`)

- `MiniGridRunner` — auto-attaches `SubgoalDetector.for_doorkey()` when env id contains `DoorKey`
- `run_minigrid_batch()` — shared session across episodes; exports replay to `data/minigrid/replay/top_transitions.jsonl`
- `run_minigrid_baseline_batch()` — Phase 1 policy, separate data dir

**Default envs:** `MiniGrid-Empty-8x8-v0`, `MiniGrid-DoorKey-8x8-v0`, `MiniGrid-FourRooms-v0`.

### 5.3 BabyAI runner (`babyai_runner.py`)

- Reads `env.unwrapped.mission` after reset
- `SubgoalDetector.from_mission(mission)` for tagging
- Stores `metadata.mission` on transitions
- Replay export: `data/babyai/replay/top_transitions.jsonl`

**Default env:** `BabyAI-GoToRedBallGrey-v0` (also `BabyAI-GoToRedBall-v0`, `BabyAI-PickupLoc-v0`, etc. via minigrid registry).

### 5.4 ARC exploration runner (`arc_exploration.py`)

`ArcExplorationRunner` wraps `ArcAGI3Runner` (mock / replay / live):

- `ExplorationPolicyV2` + dual-key novelty when object scenes enabled
- Level-change subgoal (`level_progress`) tracked via `level_id` changes
- Loop counting via repeated hashes in recent window
- Per-episode exploration graph: `data/arc_exploration/graphs/{episode_id}.json`
- Agent version: `asra-v0.5-phase3`

`build_arc_exploration_graphs(transition_dir, output_dir)` — one graph JSON per episode JSONL.

---

## 6. CLI commands

All commands run from `asra-arc/` after `pip install -e '.[dev,exploration]'`.

| Command | Purpose |
|---------|---------|
| `python -m asra run-minigrid` | MiniGrid batch with exploration v2 |
| `python -m asra run-babyai` | BabyAI batch with subgoal tagging |
| `python -m asra run-arc-exploration` | Single ARC episode with Phase 3 engine |
| `python -m asra eval-doorkey` | DoorKey benchmark: v2 vs Phase 1 baseline |
| `python -m asra build-exploration-graph` | Build graph JSON from transition dir |

### 6.1 `run-minigrid`

```bash
python -m asra run-minigrid \
  --env MiniGrid-DoorKey-8x8-v0 \
  --episodes 20 \
  --max-steps 300 \
  --data-dir data/minigrid \
  --seed 42 \
  --object-scenes    # optional Phase 2 scenes on states
```

### 6.2 `run-babyai`

```bash
python -m asra run-babyai \
  --env BabyAI-GoToRedBallGrey-v0 \
  --episodes 10 \
  --max-steps 200 \
  --data-dir data/babyai \
  --seed 42
```

### 6.3 `run-arc-exploration`

```bash
python -m asra run-arc-exploration --mock --max-steps 50 --data-dir data/arc_exploration
python -m asra run-arc-exploration --replay-file data/raw/sample_arc_agi3_replay.json --max-steps 50
```

### 6.4 `eval-doorkey`

```bash
python -m asra eval-doorkey \
  --env MiniGrid-DoorKey-8x8-v0 \
  --episodes 20 \
  --max-steps 300 \
  --output data/analysis/phase3/doorkey_benchmark.json
```

### 6.5 `build-exploration-graph`

```bash
python -m asra build-exploration-graph \
  --input-dir data/minigrid/transitions \
  --output data/minigrid/graphs/exploration_graph.json
```

---

## 7. Evaluation scripts

| Script | Output | Metrics |
|--------|--------|---------|
| `scripts/eval_phase3_minigrid.py` | `data/analysis/phase3/minigrid_summary.json` | Episodes, steps, success rate, revisit rate, unique nodes |
| `scripts/eval_phase3_doorkey_benchmark.py` | `data/analysis/phase3/doorkey_benchmark.json` | Side-by-side v2 vs baseline: success, revisit, unique nodes, strategy reuse |
| `scripts/eval_phase3_babyai.py` | `babyai_summary.json`, `babyai_subgoals.csv` | Subgoal accuracy (replay oracle), success rate |
| `scripts/eval_phase3_arc_ablation.py` | `data/analysis/phase3/arc_ablation.json` | Baseline vs Phase 3: unique nodes, loop count, reward |

**BabyAI subgoal accuracy:** logged `subgoal_complete_id` events compared to oracle replay of the same action sequence through `SubgoalDetector` — 100% match on successful GoTo episodes in smoke tests.

**DoorKey benchmark:** runs v2 to `data/minigrid/doorkey_v2/` and baseline to `data/minigrid/doorkey_baseline/` with identical seeds.

---

## 8. Data paths

| Path | Contents |
|------|----------|
| `data/minigrid/episodes/` | Episode summaries (JSON) |
| `data/minigrid/transitions/` | Per-episode JSONL transition logs |
| `data/minigrid/replay/top_transitions.jsonl` | Priority replay export |
| `data/minigrid/graphs/exploration_graph.json` | Batch exploration graph |
| `data/minigrid/doorkey_v2/` | DoorKey benchmark — Phase 3 runs |
| `data/minigrid/doorkey_baseline/` | DoorKey benchmark — Phase 1 runs |
| `data/babyai/` | Same layout for BabyAI |
| `data/arc_exploration/transitions/` | ARC Phase 3 transition logs |
| `data/arc_exploration/graphs/` | Per-episode exploration graphs |
| `data/analysis/phase3/` | Benchmark and eval JSON/CSV reports |

---

## 9. Transition metadata (Phase 3 extension)

Phase 3 enriches Phase 1 transitions without breaking schema:

```json
{
  "metadata": {
    "agent_version": "asra-v0.5-phase3",
    "policy": "exploration_v2",
    "minigrid_action": "forward",
    "mission": "go to the red ball",
    "exploration": {
      "novelty": 0.82,
      "usefulness": 0.45,
      "visit_count_before": 2,
      "frontier_node": true,
      "dead_end": false,
      "subgoal_id": "goto_target",
      "subgoal_index": 0,
      "subgoal_complete": true,
      "subgoal_complete_id": "goto_target",
      "strategy_hint": "door_key_sequence_v1",
      "loop_detected": false
    },
    "object_scenes_attached": false
  }
}
```

**ARC-only fields:** `loop_detected`, `dead_end_score` (from Phase 1 dead-end detector).

**Action names:** MiniGrid/BabyAI env steps use ASRA `ACTION1`–`ACTION7` in `action.name`; human-readable MiniGrid label in `metadata.minigrid_action`.

---

## 10. Tests

| File | Coverage |
|------|----------|
| `test_exploration_graph.py` | Graph ingest, frontiers, unique nodes |
| `test_exploration_novelty.py` | Novelty monotonicity, dead-end penalty |
| `test_exploration_policy.py` | Policy v2 selection, strategy bias |
| `test_exploration_replay.py` | Heap keeps highest priority |
| `test_exploration_subgoals.py` | Mission parser |
| `test_exploration_subgoal_detector.py` | Detector state machine, DoorKey key pickup |
| `test_exploration_strategies.py` | Match, bias, extract from WIN episode |
| `test_exploration_arc.py` | Mock ARC exploration episode + metadata |

```bash
cd asra-arc && pytest tests/test_exploration_*.py -q
# 18 exploration tests; 60 total project tests
```

---

## 11. Kaggle integration

**Notebook:** [`asra-phase-3-arc-prize-2026.ipynb`](asra-phase-3-arc-prize-2026.ipynb)  
**Agent source:** [`asra_phase3_my_agent.py`](asra_phase3_my_agent.py)  
**Build script:** `asra-arc/scripts/build_phase3_kaggle_notebook.py`  
**Submit:** `kaggle-notebooks/phase3/push_and_submit.py` or `./submit.sh all`

**Kernel slug:** `ilakkmanoharan/asra-phase-3-arc-prize-2026`  
**Agent tag:** `asra-v0.5-phase3`

The competition agent embeds:
- Phase 2 `compact_scene()` object hints (unchanged)
- Phase 3 `CompactExplorationHints` — visit-count novelty, edge stats, loop penalty
- Combined scoring in `ASRAExplorer.choose_action()` with weights `ASRA_OBJECT_HINT_WEIGHT` (0.35) and `ASRA_EXPLORATION_HINT_WEIGHT` (0.45)

Standalone hints module (for reference): [`../asra_phase3_exploration_hints.py`](../asra_phase3_exploration_hints.py)

**Regenerate notebook after agent edits:**

```bash
cd asra-arc && python scripts/build_phase3_kaggle_notebook.py
```

**Local self-test:**

```bash
python kaggle-notebooks/phase3/asra_phase3_my_agent.py --self-test
```

---

## 12. Milestone deliverable map

### Milestone 3A — MiniGrid foundation

| Spec task | Implementation |
|-----------|----------------|
| `[exploration]` extra | `pyproject.toml` → `exploration = ["gymnasium", "minigrid"]` |
| `MiniGridRunner` | `minigrid_runner.py` + `runner_core.py` |
| `ExplorationGraph` + `VisitationMemory` | `exploration_graph.py`, `visitation_memory.py` + tests |
| `NoveltyScore` v1 | `novelty.py` |
| CLI `run-minigrid` | `__main__.py` |

### Milestone 3B — Useful exploration

| Spec task | Implementation |
|-----------|----------------|
| `UsefulnessScore` | `usefulness.py` |
| `ExplorationPolicyV2` | `policy_v2.py` |
| DoorKey eval | `eval_phase3_doorkey_benchmark.py`, CLI `eval-doorkey` |
| Replay buffer export | `replay.py` → `{data_dir}/replay/top_transitions.jsonl` |
| Phase 1 baseline | `Phase1PolicyAdapter`, `run_minigrid_baseline_batch()` |

### Milestone 3C — BabyAI subgoals

| Spec task | Implementation |
|-----------|----------------|
| Mission parser | `parse_babyai_mission()` in `subgoals.py` |
| `SubgoalDetector` | `SubgoalDetector` class + completion events in metadata |
| `StrategyLibrary` v1 | `strategies.py` — DoorKey pattern extract + reuse |
| BabyAI eval harness | `babyai_runner.py`, `eval_phase3_babyai.py`, CLI `run-babyai` |

### Milestone 3D — ARC-AGI-3 integration

| Spec task | Implementation |
|-----------|----------------|
| Exploration graph from ARC logs | `ArcExplorationRunner`, `build_arc_exploration_graphs()` |
| Object-augmented novelty | Dual-key in `novelty.py` + `include_object_scenes` on ARC runner |
| Ablation script | `eval_phase3_arc_ablation.py` |
| Kaggle hints | `asra_phase3_exploration_hints.py` |
| CLI | `run-arc-exploration` |

---

## 13. Public API (`asra.exploration`)

```python
from asra.exploration import (
    ArcExplorationRunner,
    BabyAIRunner,
    ExplorationGraph,
    ExplorationPolicyV2,
    MiniGridRunner,
    Phase1PolicyAdapter,
    StrategyLibrary,
    SubgoalDetector,
    TransitionReplayBuffer,
    VisitationMemory,
    build_arc_exploration_graphs,
    build_exploration_graph_from_transitions,
    run_babyai_batch,
    run_minigrid_baseline_batch,
    run_minigrid_batch,
)
```

---

## 14. Known limitations & next steps

| Item | Notes |
|------|-------|
| DoorKey success rate | Benchmark infrastructure complete; higher WIN rates may need longer batches or policy tuning |
| FourRooms eval | Runner supports env id; no dedicated report script yet |
| Live ARC-AGI-3 | `ArcExplorationRunner` supports live backend; requires `ASRA_ARC_AGI3_*` credentials |
| Kaggle notebook | ✅ `asra-phase-3-arc-prize-2026.ipynb` + push/submit scripts |
| Phase 4 | Action semantics module — next roadmap phase |

**Suggested next work:** push notebook to Kaggle and submit; run DoorKey benchmark at `--episodes 100` for stable metrics.

---

## 15. Related documents

| Document | Location |
|----------|----------|
| Phase 3 conceptual article | [asra-phase3-exploration-memory-navigation.md](asra-phase3-exploration-memory-navigation.md) |
| Phase 3 specification (detailed) | [phase3-exploration-memory-navigation.md](phase3-exploration-memory-navigation.md) |
| Phase 2 (object scenes) | [../phase2/asra-phase2-object-centric-reasoning.md](../phase2/asra-phase2-object-centric-reasoning.md) |
| Library README | `asra-arc/README.md` (Phase 3 section) |
| Kaggle hints source | [../asra_phase3_exploration_hints.py](../asra_phase3_exploration_hints.py) |
