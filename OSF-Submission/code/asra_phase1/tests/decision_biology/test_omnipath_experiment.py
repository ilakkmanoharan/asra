from pathlib import Path

from asra.decision_biology.experiment import run_omnipath_prior_experiment
from asra.decision_biology.omnipath_loader import load_signaling_subgraph


def test_load_subgraph_fallback():
    genes, edges, meta = load_signaling_subgraph(cache_path=Path("/nonexistent/cache.parquet"))
    assert len(genes) >= 8
    assert len(edges) >= 8
    assert meta["source"] in ("fallback_mapk", "omnipath_api", "cache")


def test_run_experiment_smoke(tmp_path: Path):
    report = run_omnipath_prior_experiment(tmp_path, num_episodes=3, max_steps=5, seed=1)
    assert report["num_transitions"] == 15
    assert (tmp_path / "analysis" / "omnipath_prior_report.json").exists()
    assert (tmp_path / "graphs" / "prior_world_model_m0.json").exists()
