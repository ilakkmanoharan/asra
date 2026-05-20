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

## Limitations

- The default backend is a mock ARC-style environment.
- Live ARC-AGI-3 API semantics are intentionally abstracted behind `EnvironmentBackend`.
- The baseline policy explores; it is not a solver and does not optimize for winning yet.

## Phase 2 Next Steps

- Add a real ARC-AGI-3 backend adapter.
- Improve action effect modeling and novelty search.
- Add richer graph analytics and experiment tracking.
