# ASRA v0.1 for ARC-AGI-3

ASRA, the Adaptive Scientific Reasoning Architecture, is a baseline observation layer for ARC-AGI-3 interactive environments. Phase 1 focuses on infrastructure: observe frames, try unknown actions, compare state transitions, log them, build a state graph, replay episodes, and export datasets.

## What Phase 1 Does

- Normalizes ARC-AGI-3 JSON frames into a validated internal frame format.
- Runs a baseline exploration agent without assuming action semantics.
- Logs every `state -> action -> next_state -> reward -> terminal_state -> metadata` transition.
- Computes grid diffs and deterministic SHA-256 state hashes.
- Builds a state graph from logged transitions.
- Exports JSONL, Parquet, CSV summaries, and graph JSON.
- Provides a CLI replay viewer and optional Streamlit app.

The current runner includes a mock ARC-style environment so the full pipeline is reproducible before connecting a live ARC-AGI-3 backend.

## Installation

```bash
cd asra-arc
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev,viewer,graph]'
```

Copy `.env.example` if you need live ARC-AGI-3 credentials later.

## Run One Episode

```bash
python -m asra run-episode --game-id GAME_ID --level-id LEVEL_ID --max-steps 200 --output-dir data/episodes
```

## Run Batch Episodes

```bash
python -m asra run-batch --num-episodes 50 --max-steps 200
```

## Build Graph

```bash
python -m asra build-graph --input-dir data/transitions --output data/graphs/state_graph.json
```

## Replay

```bash
python -m asra replay --episode-id EPISODE_ID
```

Optional Streamlit viewer:

```bash
streamlit run src/asra/viewer/streamlit_app.py
```

## Export Dataset

```bash
python -m asra export-dataset --input-dir data/transitions --output-dir data/exports
```

Outputs:

- `data/exports/asra_v0_1_transitions.jsonl`
- `data/exports/asra_v0_1_transitions.parquet`
- `data/exports/asra_v0_1_episode_summary.csv`
- `data/exports/asra_v0_1_state_graph.json`

## Hash stability analysis

State hashes must be stable: the same grid (values and shape) must always map to the same hash, with no dependence on timestamps, episode IDs, or other row metadata. That underpins the state graph, cycle detection, and replay.

After exporting transitions, run the analysis script on your JSONL (defaults shown):

```bash
pip install '.[analysis]'   # optional: matplotlib plots + full graph PNG
python scripts/hash_stability_analysis.py \
  data/exports/asra_v0_1_transitions.jsonl \
  --out-dir data/analysis/hash_stability
```

It writes:

- `data/analysis/hash_stability/hash_stability_report.txt` — summary and pass/fail
- `data/analysis/hash_stability/unstable_grids.json` — same grid with multiple hashes (if any)
- `data/analysis/hash_stability/state_statistics.csv` — visit counts per `state_hash`
- `data/analysis/hash_stability/transition_graph.graphml` — transition graph (requires `networkx`, included in `[graph]` / `[analysis]`)
- Histogram / graph images when `matplotlib` is installed (`[analysis]`); otherwise see `visualization_skipped.txt`

Implementation: `scripts/hash_stability_analysis.py`.

## Transition Schema

Each row includes episode, game, level, step, normalized state, action, next state, reward, terminal flag, grid diff, state hashes, policy name, agent version, and metadata.

Example transition row:

```json
{"state":{"grid":[[0]],"state_hash":"..."},"action":{"name":"ACTION1","index":1},"next_state":{"grid":[[1]],"state_hash":"..."},"reward":0.0,"terminal_state":false,"metadata":{"agent_version":"asra-v0.1","policy":"simple_exploration"}}
```

## Backends (Phase 1)

| Mode | Command flag | Use case |
|------|----------------|----------|
| Mock | `--mock` (default offline) | CI, dev, reproducible pipeline |
| Replay | `--replay-file data/raw/sample_arc_agi3_replay.json` | Offline ARC-AGI-3 frame replay |
| Live | `--live` | Real API when `ASRA_ARC_AGI3_ENDPOINT` + `ASRA_ARC_AGI3_API_KEY` are set |

Generate the sample replay file:

```bash
python scripts/generate_sample_replay.py
python -m asra run-episode --replay-file data/raw/sample_arc_agi3_replay.json --max-steps 20
```

Action-effect reports (spec §7) are saved under `data/analysis/action_reports/{state_hash}.json`.

## Visual replay (Priority 1)

```bash
pip install -e '.[viewer]'
streamlit run src/asra/viewer/streamlit_app.py
```

Three tabs in one app:

| Tab | Purpose |
|-----|---------|
| **Replay** | Step through logged JSONL (before · after · diff) |
| **ASRA Lab** | Play the mock 3×3 world yourself (same rules as the backend) |
| **Animated replay** | Auto-play an episode frame-by-frame (~300 ms default) |
| **Guided tutorial (10 steps)** | Slow walkthrough of first 10 log frames with action formulas and next-step previews |

Color grids: before · after · diff overlay · action · reward · terminal status.

## State graph visualization (Priority 2)

```bash
pip install -e '.[analysis]'
python -m asra visualize-graph
```

Writes `data/analysis/graph_viz/state_graph.png` and `graph_analysis.json`.

## Large-scale data (Priority 3)

```bash
python -m asra run-scale --num-episodes 10000 --max-steps 50
python -m asra export-dataset
python -m asra visualize-graph
```

## Phase 1 complete (one command)

Runs terminal-demo episode, mock + replay episodes, small batch, export, graph, and hash stability check:

```bash
pip install -e '.[dev,graph,analysis]'
python -m asra complete-phase1
```

Or step by step:

```bash
python scripts/generate_sample_replay.py
python -m asra run-episode --mock --terminal-demo --max-steps 12
python -m asra run-episode --replay-file data/raw/sample_arc_agi3_replay.json --max-steps 20
python -m asra run-batch --mock --num-episodes 5 --max-steps 50
python -m asra export-dataset
python -m asra build-graph
python scripts/hash_stability_analysis.py data/exports/asra_v0_1_transitions.jsonl
```

### Phase 1 definition of done

- [x] `pytest tests/` — all pass (24 tests)
- [x] Episodes on mock, replay (`data/raw/sample_arc_agi3_replay.json`), and exported transitions
- [x] At least one episode ending in `WIN` (`--terminal-demo`)
- [x] `data/exports/asra_v0_1_transitions.jsonl` aggregates all `data/transitions/*.jsonl`
- [x] Hash stability report: **PASSED**
- [x] `data/analysis/action_reports/` — action-test JSON per visited state
- [x] Notebooks `notebooks/01_inspect_arc_frames.ipynb` and `02_analyze_agent_dataset.ipynb`

## Limitations

- Live ARC-AGI-3 requires your competition/API endpoint; use replay or mock until credentials are configured.
- The baseline policy explores; it is not a solver and does not optimize for winning yet.

## Decision Biology (OmniPath prior experiment)

First biological-domain run: OmniPath signaling interactions as world-model prior **M₀**, gene-activity states, perturbation actions.

```bash
pip install -e '.[biology]'
python scripts/decision_biology/run_omnipath_prior_experiment.py
```

- Code: `src/asra/decision_biology/`
- Data: `data/decision_biology/omnipath/`
- Write-up: `private/documents/phase2-decision-biology/omnipath/results.md`

## Phase 2 Next Steps

- Action semantics inference (roadmap Phase 2 / 4).
- Original ARC and symbolic abstraction modules.
- Stronger exploration — not required for Phase 1 completion.
