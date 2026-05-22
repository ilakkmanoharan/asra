# LINCS L1000 data for ASRA Decision Biology

Experiment outputs (`exports/`, `graphs/`, `analysis/`) are version-controlled. **Raw** LINCS Level-2 GEX files are not in git (GEO [GSE92742](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE92742); some files exceed GitHub’s 100 MB limit).

## Obtain raw data

1. Download Level-2 delta GCTX and metadata per `src/asra/decision_biology/lincs_loader.py`.
2. Place files under `raw/` (e.g. `level2_delta_978.gctx` or `.gctx.gz`, `gene_info.txt`, `inst_info.txt`, `sig_info.txt`).
3. Run from `asra-arc`:

```bash
pip install -e '.[biology]'
python scripts/decision_biology/run_decision_biology_experiments.py
```

Exported transitions and learned `M_t` graphs are written to `exports/` and `graphs/`.
