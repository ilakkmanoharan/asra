from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

DEFAULT_CACHE = Path("data/decision_biology/omnipath/raw/signaling_interactions.parquet")


def _fetch_omnipath_interactions(max_rows: int = 2500) -> pd.DataFrame:
    try:
        from omnipath.interactions import OmniPath
    except ImportError as exc:
        raise ImportError("Install biology extras: pip install -e '.[biology]'") from exc

    ia = OmniPath()
    df = ia.get(
        directed=True,
        genesymbols=True,
        license="academic",
        limit=max_rows,
        resources=["SIGNOR", "PhosphoPoint", "PhosphoSite"],
    )
    if df is None or df.empty:
        raise RuntimeError("OmniPath returned no interactions")
    src_col = "source_genesymbol" if "source_genesymbol" in df.columns else "source"
    tgt_col = "target_genesymbol" if "target_genesymbol" in df.columns else "target"
    out = df[[src_col, tgt_col]].copy()
    out = out.rename(columns={src_col: "source", tgt_col: "target"})
    return out.dropna(subset=["source", "target"])


def _fallback_signaling_edges() -> pd.DataFrame:
    """Small RAS–MAPK-style subgraph when OmniPath API is unavailable."""
    edges = [
        ("EGF", "EGFR"), ("EGFR", "GRB2"), ("GRB2", "SOS1"), ("SOS1", "KRAS"),
        ("KRAS", "RAF1"), ("RAF1", "MAP2K1"), ("MAP2K1", "MAPK1"), ("MAPK1", "ELK1"),
        ("EGFR", "PIK3CA"), ("PIK3CA", "AKT1"), ("AKT1", "MTOR"), ("MTOR", "RPS6KB1"),
        ("MAPK1", "FOS"), ("MAPK1", "JUN"), ("KRAS", "PIK3CA"),
    ]
    return pd.DataFrame(edges, columns=["source", "target"])


def load_signaling_subgraph(
    cache_path: Path | None = None,
    *,
    max_genes: int = 32,
    refresh: bool = False,
) -> tuple[list[str], list[tuple[str, str]], dict[str, Any]]:
    """
    Return (genes, directed_edges, metadata) for a signaling subgraph.
    Uses cached Parquet when present; otherwise OmniPath API or built-in fallback.
    """
    cache = cache_path or DEFAULT_CACHE
    meta: dict[str, Any] = {"source": "cache", "cache_path": str(cache)}

    if cache.exists() and not refresh:
        df = pd.read_parquet(cache)
        meta["source"] = "cache"
    else:
        try:
            df = _fetch_omnipath_interactions()
            meta["source"] = "omnipath_api"
            cache.parent.mkdir(parents=True, exist_ok=True)
            df.to_parquet(cache, index=False)
        except Exception as exc:
            df = _fallback_signaling_edges()
            meta["source"] = "fallback_mapk"
            meta["fetch_error"] = str(exc)

    edges = [(str(r.source), str(r.target)) for r in df.itertuples(index=False)]
    genes = sorted({g for u, v in edges for g in (u, v)})
    if len(genes) > max_genes:
        # Keep highest-degree nodes
        degree: dict[str, int] = {g: 0 for g in genes}
        for u, v in edges:
            degree[u] += 1
            degree[v] += 1
        keep = set(sorted(degree, key=degree.get, reverse=True)[:max_genes])
        edges = [(u, v) for u, v in edges if u in keep and v in keep]
        genes = sorted(keep)

    meta["n_genes"] = len(genes)
    meta["n_edges"] = len(edges)
    meta["genes"] = genes
    return genes, edges, meta
