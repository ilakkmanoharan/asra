from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_RAW = Path("data/decision_biology/lincs/raw")
GCTX_NAME = "level2_delta_978.gctx"
GCTX_GZ = "level2_delta_978.gctx.gz"


def _ensure_gctx(raw_dir: Path) -> Path:
    gctx = raw_dir / GCTX_NAME
    gz = raw_dir / GCTX_GZ
    if gctx.exists():
        return gctx
    if gz.exists():
        import gzip
        import shutil

        with gzip.open(gz, "rb") as fin, open(gctx, "wb") as fout:
            shutil.copyfileobj(fin, fout)
        return gctx
    raise FileNotFoundError(
        f"LINCS GCTX not found. Download {GCTX_GZ} from GSE92742 GEO supplement to {raw_dir}"
    )


def list_signature_ids(
    raw_dir: Path | None = None,
    *,
    cell_pattern: str = "MCF7",
    time_h: int | None = None,
    max_signatures: int = 120,
) -> tuple[list[str], dict[str, Any]]:
    """Return GCTX column ids (Level 2 delta) filtered by cell line and optional time in column id string."""
    raw_dir = raw_dir or DEFAULT_RAW
    _ensure_gctx(raw_dir)
    from cmapPy.pandasGEXpress.parse import parse

    col_meta = parse(str(raw_dir / GCTX_NAME), col_meta_only=True)
    ids = []
    pat_cell = re.compile(rf"_{cell_pattern}_", re.I)
    pat_time = re.compile(rf"_{time_h}H", re.I) if time_h else None
    for cid in col_meta.index.astype(str):
        if not pat_cell.search(cid):
            continue
        if pat_time and not pat_time.search(cid):
            continue
        ids.append(cid)
        if len(ids) >= max_signatures:
            break
    if len(ids) < 10:
        for cid in col_meta.index.astype(str):
            if pat_cell.search(cid):
                ids.append(cid)
            if len(ids) >= max_signatures:
                break
    meta = {
        "source": "GEO_GSE92742_Level2_GEX_delta",
        "gctx": str(raw_dir / GCTX_NAME),
        "cell_pattern": cell_pattern,
        "time_h": time_h,
        "n_signatures": len(ids),
    }
    return ids, meta


def load_landmark_expression(
    signature_ids: list[str],
    raw_dir: Path | None = None,
    *,
    max_genes: int = 48,
) -> tuple[list[str], pd.DataFrame, dict[str, Any]]:
    """
    Load landmark-gene expression delta matrix for given GCTX column ids.
    Returns (gene_symbols, matrix columns=sig_id, values=float).
    """
    raw_dir = raw_dir or DEFAULT_RAW
    gctx_path = _ensure_gctx(raw_dir)
    gene_info = pd.read_csv(raw_dir / "gene_info.txt", sep="\t")
    landmarks = gene_info[gene_info["pr_is_lm"] == 1].head(max_genes)
    gene_symbols = landmarks["pr_gene_symbol"].tolist()

    from cmapPy.pandasGEXpress.parse import parse

    gct = parse(str(gctx_path), cid=signature_ids)
    df = gct.data_df.copy()
    # GCTX rows are 0..977 in landmark-only file
    if len(df) >= len(gene_symbols):
        df = df.iloc[: len(gene_symbols)]
    df.index = gene_symbols[: len(df)]
    meta = {"n_genes": len(df), "n_signatures": len(signature_ids)}
    return gene_symbols, df, meta


def perturbation_name_from_cid(cid: str) -> str:
    """Extract BRD compound id or unique profile label from GCTX column id."""
    m = re.search(r"(BRD-[A-Z0-9-]+)", cid)
    if m:
        return m.group(1)
    base = cid.split(":")[0]
    well = cid.split(":")[-1] if ":" in cid else "sig"
    return f"{base.split('_')[0]}_{well}"
