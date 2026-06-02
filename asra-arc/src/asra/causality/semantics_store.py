from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from asra.causality.effect_summarizer import ActionEffectSummarizer
from asra.causality.hypothesis_tester import HypothesisTester
from asra.causality.schemas import ActionEffectSignature
from asra.causality.transition_model import CausalTransitionModel
from asra.causality.uncertainty import UncertaintyScorer
from asra.utils.serialization import read_json, write_json


class SemanticsStore:
    """Persistent per-game action semantics tables."""

    def __init__(self) -> None:
        self.summarizer = ActionEffectSummarizer()
        self.model = CausalTransitionModel()
        self.hypotheses = HypothesisTester()
        self.uncertainty = UncertaintyScorer()
        self._signatures: dict[tuple[str, str, str], ActionEffectSignature] = {}

    def ingest_transition(self, transition: dict[str, Any]) -> ActionEffectSignature | None:
        self.summarizer.observe_transition(transition)
        self.model.observe_transition(transition)
        game_id = str(transition.get("game_id") or "unknown")
        state = transition.get("state") or {}
        state_hash = str(state.get("state_hash") or "")
        action = str((transition.get("action") or {}).get("name") or transition.get("action") or "")
        if not state_hash or not action:
            return None
        sig = self.summarizer.summarize(game_id, state_hash, action)
        self._signatures[(game_id, state_hash, action)] = sig
        hyp = self.hypotheses.upsert_from_signature(sig)
        transition.setdefault("metadata", {})["causality"] = self.causality_metadata(sig, hyp.hypothesis_id)
        return sig

    def causality_metadata(self, signature: ActionEffectSignature, hypothesis_id: str | None = None) -> dict[str, Any]:
        hyp = self.hypotheses.get(hypothesis_id) if hypothesis_id else None
        status = hyp.status if hyp else None
        pred = self.model.predict(signature.game_id, signature.state_hash, signature.action)
        return {
            "effect_signature_id": signature.signature_id,
            "semantic_label": signature.semantic_label,
            "confidence": signature.confidence,
            "uncertainty": self.uncertainty.score(signature, hypothesis_status=status),
            "hypothesis_id": hypothesis_id,
            "predicted_changed_cells": pred.predicted_changed_cells,
            "predicted_object_delta": pred.predicted_object_delta,
            "transform_histogram": signature.transform_histogram,
            "observation_count": signature.observation_count,
        }

    def get_signature(self, game_id: str, state_hash: str, action: str) -> ActionEffectSignature | None:
        return self._signatures.get((game_id, state_hash, action)) or self.summarizer.summarize(
            game_id, state_hash, action
        )

    def save(self, output_dir: str | Path) -> dict[str, Path]:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        by_game: dict[str, list[dict[str, Any]]] = {}
        for sig in self.summarizer.summarize_all():
            by_game.setdefault(sig.game_id, []).append(sig.to_dict())
        paths: dict[str, Path] = {}
        for game_id, rows in by_game.items():
            safe = game_id.replace("/", "_")
            path = out / f"{safe}_semantics.json"
            write_json(path, {"game_id": game_id, "signatures": rows, "hypotheses": self.hypotheses.to_dict()})
            paths[game_id] = path
        index_path = out / "index.json"
        write_json(index_path, {"games": list(by_game.keys()), "signature_count": sum(len(v) for v in by_game.values())})
        paths["index"] = index_path
        return paths

    @classmethod
    def load(cls, semantics_dir: str | Path) -> SemanticsStore:
        store = cls()
        root = Path(semantics_dir)
        for path in sorted(root.glob("*_semantics.json")):
            payload = read_json(path)
            for row in payload.get("signatures") or []:
                sig = ActionEffectSignature(**row)
                key = (sig.game_id, sig.state_hash, sig.action)
                store._signatures[key] = sig
                store.summarizer._observations[key] = [{"changed_cells": sig.cell_change_mean}] * sig.observation_count
        return store
