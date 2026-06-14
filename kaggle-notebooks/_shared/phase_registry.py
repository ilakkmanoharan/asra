"""Phase metadata for Kaggle gateway notebooks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMP = "arc-prize-2026-arc-agi-3"


@dataclass(frozen=True)
class PhaseConfig:
    number: int
    agent_tag: str
    kernel_slug: str
    title: str
    notebook_name: str
    phase_dir: Path
    my_agent: Path
    template_agent: Path

    @property
    def notebook_path(self) -> Path:
        return self.phase_dir / self.notebook_name


PHASES: dict[int, PhaseConfig] = {
    1: PhaseConfig(
        1,
        "asra-v0.1-phase1",
        "ilakkmanoharan/asra-phase-1-arc-prize-2026",
        "ASRA Phase 1 — ARC Prize 2026",
        "asra-phase-1-arc-prize-2026.ipynb",
        ROOT / "phase1",
        ROOT / "phase1" / "asra_phase1_my_agent.py",
        ROOT / "phase1" / "asra_phase1_kaggle_template_agent.py",
    ),
    2: PhaseConfig(
        2,
        "asra-v0.4-phase2",
        "ilakkmanoharan/asra-phase-2-arc-prize-2026",
        "ASRA Phase 2 — ARC Prize 2026",
        "asra-phase-2-arc-prize-2026.ipynb",
        ROOT / "phase2",
        ROOT / "asra_phase2_my_agent.py",
        ROOT / "phase2" / "asra_phase2_kaggle_template_agent.py",
    ),
    3: PhaseConfig(
        3,
        "asra-v0.5-phase3",
        "ilakkmanoharan/asra-phase-3-arc-prize-2026",
        "ASRA Phase 3 — ARC Prize 2026",
        "asra-phase-3-arc-prize-2026.ipynb",
        ROOT / "phase3",
        ROOT / "phase3" / "asra_phase3_my_agent.py",
        ROOT / "phase3" / "asra_phase3_kaggle_template_agent.py",
    ),
    4: PhaseConfig(
        4,
        "asra-v0.6-phase4",
        "ilakkmanoharan/asra-phase-4-arc-prize-2026",
        "ASRA Phase 4 — ARC Prize 2026",
        "asra-phase-4-arc-prize-2026.ipynb",
        ROOT / "phase4",
        ROOT / "phase4" / "asra_phase4_my_agent.py",
        ROOT / "phase4" / "asra_phase4_kaggle_template_agent.py",
    ),
    5: PhaseConfig(
        5,
        "asra-v0.7-phase5",
        "ilakkmanoharan/asra-phase-5-arc-prize-2026",
        "ASRA Phase 5 — ARC Prize 2026",
        "asra-phase-5-arc-prize-2026.ipynb",
        ROOT / "phase5",
        ROOT / "phase5" / "asra_phase5_my_agent.py",
        ROOT / "phase5" / "asra_phase5_kaggle_template_agent.py",
    ),
    6: PhaseConfig(
        6,
        "asra-v0.8-phase6",
        "ilakkmanoharan/asra-phase-6-arc-prize-2026",
        "ASRA Phase 6 — ARC Prize 2026",
        "asra-phase-6-arc-prize-2026.ipynb",
        ROOT / "phase6",
        ROOT / "phase6" / "asra_phase6_my_agent.py",
        ROOT / "phase6" / "asra_phase6_kaggle_template_agent.py",
    ),
    7: PhaseConfig(
        7,
        "asra-v0.85-phase7",
        "ilakkmanoharan/asra-phase-7-arc-prize-2026",
        "ASRA Phase 7 — ARC Prize 2026",
        "asra-phase-7-arc-prize-2026.ipynb",
        ROOT / "phase7",
        ROOT / "phase7" / "asra_phase7_my_agent.py",
        ROOT / "phase7" / "asra_phase7_kaggle_template_agent.py",
    ),
    8: PhaseConfig(
        8,
        "asra-v0.9-phase8",
        "ilakkmanoharan/asra-phase-8-arc-prize-2026",
        "ASRA Phase 8 — ARC Prize 2026",
        "asra-phase-8-arc-prize-2026.ipynb",
        ROOT / "phase8",
        ROOT / "phase8" / "asra_phase8_my_agent.py",
        ROOT / "phase8" / "asra_phase8_kaggle_template_agent.py",
    ),
    9: PhaseConfig(
        9,
        "asra-v1.0-phase9",
        "ilakkmanoharan/asra-phase-9-arc-prize-2026",
        "ASRA Phase 9 — ARC Prize 2026",
        "asra-phase-9-arc-prize-2026.ipynb",
        ROOT / "phase9",
        ROOT / "phase9" / "asra_phase9_my_agent.py",
        ROOT / "phase9" / "asra_phase9_kaggle_template_agent.py",
    ),
}


def get_phase(number: int) -> PhaseConfig:
    if number not in PHASES:
        raise KeyError(f"Unknown phase {number}; choose 1–9")
    return PHASES[number]
