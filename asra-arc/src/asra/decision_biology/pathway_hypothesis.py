from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PathwayHypothesis:
    pathway_id: str
    perturbation_class: str
    support: int = 0
    refute: int = 0
    metadata: dict[str, Any] = field(default_factory=dict)


class PathwayHypothesisEngine:
    """Phase 8: pathway-level hypotheses from perturbation-response tuples."""

    PERTURBATION_CLASSES = [
        "mechanical_stimulus",
        "signaling_inhibitor",
        "gene_overexpression",
        "knockdown",
        "pathway_activation",
    ]

    def __init__(self) -> None:
        self.hypotheses: dict[str, PathwayHypothesis] = {}

    def observe(self, cell_state_id: str, perturbation: str, response_magnitude: float) -> None:
        hid = f"{cell_state_id}:{perturbation}"
        if hid not in self.hypotheses:
            self.hypotheses[hid] = PathwayHypothesis(hid, perturbation)
        h = self.hypotheses[hid]
        if response_magnitude > 0:
            h.support += 1
        else:
            h.refute += 1

    def rank(self) -> list[PathwayHypothesis]:
        return sorted(
            self.hypotheses.values(),
            key=lambda h: h.support - h.refute,
            reverse=True,
        )
