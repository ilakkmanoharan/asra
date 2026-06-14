#!/usr/bin/env python3
"""Extract Kaggle template agents from Swarm-style my_agent.py sources."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from phase_registry import PHASES, PhaseConfig

BOOTSTRAP_MARKERS = (
    "# --- Kaggle bootstrap",
    "# --- Kaggle bootstrap (",
)
RUNTIME_END_MARKERS = (
    "def _game_ids(",
    "def scorecard_to_rows(",
    "def run_swarm(",
    "def write_submission_parquet(",
)


def _find_bootstrap_start(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        if any(m in line for m in BOOTSTRAP_MARKERS):
            return i
    for i, line in enumerate(lines):
        if line.startswith("def _working_dir("):
            return i
    raise ValueError("Could not find Kaggle bootstrap section")


def _find_runtime_start(lines: list[str]) -> int:
    for i, line in enumerate(lines):
        if "AGENTS_ROOT = _bootstrap_kaggle()" in line:
            for j in range(i + 1, len(lines)):
                stripped = lines[j].strip()
                if stripped.startswith("import numpy") or stripped.startswith("SEED ="):
                    return j
            raise ValueError("Found AGENTS_ROOT but no import numpy / SEED after bootstrap")
    raise ValueError("Could not find AGENTS_ROOT = _bootstrap_kaggle()")


def _find_agent_end(lines: list[str], start: int) -> int:
    for i in range(start, len(lines)):
        stripped = lines[i].lstrip()
        if any(stripped.startswith(m) for m in RUNTIME_END_MARKERS):
            return i
    raise ValueError("Could not find end of agent section (_game_ids / run_swarm)")


def _clean_agent_lines(lines: list[str]) -> list[str]:
    out: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("import pandas"):
            continue
        if "Agent, Swarm, AVAILABLE_AGENTS = _load_agents_runtime" in line:
            continue
        if stripped == "from agents.agent import Agent":
            continue
        out.append(line)
    return out


def extract_template(source: str, phase: PhaseConfig) -> str:
    lines = source.splitlines(keepends=True)
    bootstrap_start = _find_bootstrap_start(lines)
    runtime_start = _find_runtime_start(lines)
    agent_end = _find_agent_end(lines, runtime_start)

    pre = lines[:bootstrap_start]
    agent = _clean_agent_lines(lines[runtime_start:agent_end])
    body = "".join(pre) + "".join(agent)
    body = body.replace("class ASRAAgent(Agent):", "class MyAgent(Agent):")
    body = re.sub(
        r'^"""[\s\S]*?"""',
        f'"""ASRA Phase {phase.number} agent — Kaggle template form (auto-extracted).\n\n'
        "Spliced into submission notebook. Must expose class MyAgent.\n"
        '"""',
        body,
        count=1,
    )

    if "from agents.agent import Agent" not in body:
        anchor = "from arcengine import"
        if anchor in body:
            body = body.replace(anchor, "from agents.agent import Agent\n" + anchor, 1)
        else:
            body = "from agents.agent import Agent\n" + body

    # Drop Swarm-only imports from pre-section headers
    body = re.sub(r"^import glob\n", "", body, flags=re.M)
    body = re.sub(r"^import subprocess\n", "", body, flags=re.M)
    body = re.sub(r"^import sys\n", "", body, flags=re.M)
    body = re.sub(r"^import types\n", "", body, flags=re.M)

    return body.rstrip() + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description="Extract Kaggle template agent from my_agent.py")
    p.add_argument("--phase", type=int, action="append", dest="phases", help="Phase number (1–9); repeat for multiple")
    p.add_argument("--all", action="store_true", help="Extract all phases")
    p.add_argument("--force", action="store_true", help="Overwrite existing template agents")
    args = p.parse_args()

    numbers = sorted(PHASES) if args.all else (args.phases or [])
    if not numbers:
        p.error("Specify --phase N and/or --all")

    for n in numbers:
        phase = PHASES[n]
        if not phase.my_agent.is_file():
            print(f"Phase {n}: SKIP — missing {phase.my_agent}")
            continue
        if phase.template_agent.is_file() and not args.force:
            print(f"Phase {n}: SKIP — {phase.template_agent.name} exists (use --force)")
            continue
        source = phase.my_agent.read_text(encoding="utf-8")
        template = extract_template(source, phase)
        phase.template_agent.write_text(template, encoding="utf-8")
        print(f"Phase {n}: wrote {phase.template_agent} ({len(template)} bytes)")


if __name__ == "__main__":
    main()
