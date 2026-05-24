# ARC Prize 2026 — Local dataset mirror

Reference copy of competition resources for offline development. The **full competition bundle** (~49 MB, 148 files) must be downloaded from Kaggle.

## Competition

- **Slug:** `arc-prize-2026-arc-agi-3`
- **Page:** https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3
- **License:** Apache 2.0

## Download (requires Kaggle authentication)

### Option A — kagglehub (Python)

```python
import kagglehub
path = kagglehub.competition_download("arc-prize-2026-arc-agi-3")
print(path)
```

Requires [Kaggle API credentials](https://www.kaggle.com/docs/api) at `~/.kaggle/kaggle.json`.

### Option B — Kaggle CLI

```bash
pip install kaggle
# configure ~/.kaggle/kaggle.json
kaggle competitions download -c arc-prize-2026-arc-agi-3 -p competition/
unzip competition/arc-prize-2026-arc-agi-3.zip -d competition/
```

### Option C — Kaggle UI

Competition → **Data** → **Download All** (or use **kagglehub** snippet in the download modal).

Save extracted files under:

```text
private/kaggle-dataset/competition/
├── ARC-AGI-3-Agents/      # agent framework (also mirrored below)
├── arc_agi_3_wheels/      # .whl packages for arc_agi, arcengine
└── environment_files/     # 25 public game environments
```

Then set for local notebook runs:

```bash
export ASRA_COMP_ROOT="/path/to/asra/private/kaggle-dataset/competition"
```

## What is already in this folder

| Path | Description |
|------|-------------|
| `desc.md` | Kaggle dataset page notes (games, actions, scoring) |
| `ARC-AGI-3-Agents/` | Public git mirror of [arcprize/ARC-AGI-3-Agents](https://github.com/arcprize/ARC-AGI-3-Agents) |
| `competition/` | *(create by download)* full Kaggle competition bundle |

## Notebook integration

`private/documents/kaggle-notebooks/asra_v0_2_phase1_arc_agi3_notebook.ipynb` expects:

| Environment | `COMP_ROOT` |
|-------------|-------------|
| Kaggle kernel | `/kaggle/input/arc-prize-2026-arc-agi-3` |
| Local dev | `$ASRA_COMP_ROOT` or `../../kaggle-dataset/competition` |

On Kaggle:

1. Add competition data as notebook input.
2. Notebook installs wheels from `arc_agi_3_wheels/`.
3. Adds `ARC-AGI-3-Agents/` to `sys.path`.
4. Sets `OPERATION_MODE=COMPETITION`.
5. Registers `ASRAAgent` and runs official `Swarm`.

## Key competition facts (from dataset description)

- **Actions:** `RESET`, `ACTION1`–`ACTION7` (`ACTION6` requires x,y coordinates)
- **Frames:** JSON grids up to 64×64, cell values 0–15
- **Scoring:** completion + efficiency vs human baselines via official scorecard
- **Public games:** 25 in `environment_files/`; evaluation uses 110 private games
- **Docs:** https://docs.arcprize.org

## Status

| Item | Status |
|------|--------|
| `ARC-AGI-3-Agents` git mirror | ✅ cloned |
| Full competition bundle | ⬜ download with Kaggle credentials |
| ASRA v0.2 notebook | ✅ `../documents/kaggle-notebooks/asra_v0_2_phase1_arc_agi3_notebook.ipynb` |
