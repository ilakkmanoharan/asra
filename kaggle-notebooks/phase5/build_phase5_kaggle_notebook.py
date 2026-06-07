#!/usr/bin/env python3
"""Build Kaggle Phase 5 submission notebook from private/phase5/asra_phase5_my_agent.py."""

from __future__ import annotations

import json
from pathlib import Path


def _escape_for_triple_quote(text: str) -> str:
    return text.replace("\\", "\\\\")


def main() -> None:
    here = Path(__file__).resolve().parent
    agent_path = here / "asra_phase5_my_agent.py"
    out_path = here / "asra-phase-5-arc-prize-2026.ipynb"
    agent_code = agent_path.read_text(encoding="utf-8")
    agent_escaped = _escape_for_triple_quote(agent_code)

    bootstrap_cell = r'''import glob
import os
import shutil
import subprocess
import sys

IS_KAGGLE = os.path.exists('/kaggle/input')
COMP_SLUG = 'arc-prize-2026-arc-agi-3'
WORKING = '/kaggle/working' if IS_KAGGLE else '.'
VENV = '/tmp/asra_venv' if IS_KAGGLE else os.path.join(WORKING, 'asra_venv')
VENV_PY = os.path.join(VENV, 'bin', 'python')

if IS_KAGGLE:
    COMP_CANDIDATES = [
        f'/kaggle/input/competitions/{COMP_SLUG}',
        f'/kaggle/input/{COMP_SLUG}',
    ]
    COMP_ROOT = next((p for p in COMP_CANDIDATES if os.path.isdir(p)), COMP_CANDIDATES[0])
else:
    COMP_ROOT = os.environ.get('ASRA_COMP_ROOT', 'private/kaggle-dataset/competition')

AGENTS_ROOT = os.path.join(COMP_ROOT, 'ARC-AGI-3-Agents')
WHEELS_DIR = os.path.join(COMP_ROOT, 'arc_agi_3_wheels')
ENV_DIR = os.path.join(COMP_ROOT, 'environment_files')
RECORDINGS_DIR = os.path.join(WORKING, 'recordings')
os.makedirs(RECORDINGS_DIR, exist_ok=True)

print('IS_KAGGLE:', IS_KAGGLE)
print('COMP_ROOT:', COMP_ROOT, '| exists:', os.path.isdir(COMP_ROOT))

if IS_KAGGLE and os.path.isdir(COMP_ROOT):
    working_wheels = os.path.join(WORKING, 'wheels')
    wheels_src = os.path.join(COMP_ROOT, 'arc_agi_3_wheels')
    if os.path.isdir(wheels_src) and not os.path.isdir(working_wheels):
        shutil.copytree(wheels_src, working_wheels)
        print('Mirrored wheels ->', working_wheels)

if os.path.isdir(AGENTS_ROOT) and AGENTS_ROOT not in sys.path:
    sys.path.insert(0, AGENTS_ROOT)

wheels = sorted(glob.glob(os.path.join(WHEELS_DIR, '*.whl'))) if os.path.isdir(WHEELS_DIR) else []
if wheels:
    if not os.path.isfile(VENV_PY):
        subprocess.check_call(
            [sys.executable, '-m', 'venv', VENV, '--system-site-packages', '--without-pip'],
            stdout=subprocess.DEVNULL,
        )
        print('Created venv ->', VENV)
    py_ver = f'{sys.version_info.major}.{sys.version_info.minor}'
    SITE = os.path.join(VENV, 'lib', f'python{py_ver}', 'site-packages')
    os.makedirs(SITE, exist_ok=True)
    proc = subprocess.run(
        [sys.executable, '-m', 'pip', 'install', '--target', SITE, '--no-deps', '--upgrade', '-q', *wheels],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        print(proc.stderr)
        raise RuntimeError('Venv wheel install failed')
    os.environ['ASRA_VENV'] = VENV
    print('Installed wheels in venv:', len(wheels))
else:
    print('WARNING: wheels dir missing')

os.environ.setdefault('RECORDINGS_DIR', RECORDINGS_DIR)
os.environ.setdefault('ENVIRONMENTS_DIR', ENV_DIR if os.path.isdir(ENV_DIR) else 'environment_files')
os.environ['OPERATION_MODE'] = 'COMPETITION' if IS_KAGGLE else os.environ.get('OPERATION_MODE', 'OFFLINE')
os.environ['ASRA_AGENTS_ROOT'] = AGENTS_ROOT
print('OPERATION_MODE:', os.environ['OPERATION_MODE'])'''

    write_agent_cell = (
        "MY_AGENT_CODE = '''" + agent_escaped + "'''\n\n"
        "MY_AGENT_PATH = os.path.join(WORKING, 'my_agent.py')\n"
        "with open(MY_AGENT_PATH, 'w', encoding='utf-8') as f:\n"
        "    f.write(MY_AGENT_CODE)\n"
        "print('Wrote', MY_AGENT_PATH, '| bytes:', os.path.getsize(MY_AGENT_PATH))"
    )

    smoke_cell = r'''import subprocess

result = subprocess.run(
    [VENV_PY, MY_AGENT_PATH, '--self-test'],
    cwd=WORKING,
    env={**os.environ, 'ASRA_VENV_ACTIVE': '1', 'PYTHONNOUSERSITE': '1'},
    capture_output=True,
    text=True,
)
print(result.stdout)
if result.returncode != 0:
    print(result.stderr)
    raise RuntimeError('my_agent.py Phase 5 self-test failed')
print('Phase 5 my_agent self-test OK')'''

    parquet_cell = r'''import pandas as pd

SUBMISSION_PATH = os.path.join(WORKING, 'submission.parquet')
pd.DataFrame([{
    'game_id': 'placeholder',
    'score': 0.0,
    'levels_completed': 0,
    'actions': 0,
    'completed': False,
    'agent': 'asra-v0.7-phase5',
}]).to_parquet(SUBMISSION_PATH, index=False)
print('Wrote', SUBMISSION_PATH)
print('Outputs:', [f for f in os.listdir(WORKING) if f.endswith(('.py', '.parquet'))])'''

    nb = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.12.0"},
            "kaggle": {
                "accelerator": "none",
                "isInternetEnabled": False,
                "language": "python",
                "sourceType": "notebook",
                "competitionSources": ["arc-prize-2026-arc-agi-3"],
            },
        },
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "# ASRA Phase 5 — Kaggle submission (ARC Prize 2026)\n\n",
                    "Phase 5 adds **goal inference and hypothesis ranking** on Phase 2–4 stacks.\n\n",
                    "- Goal hypothesis templates (move, match, collect, unlock, avoid, transform)\n",
                    "- Progress detection from rewards, level changes, and action semantics\n",
                    "- Hypothesis ranking + experiment discrimination hints\n",
                    "- Venv at `/tmp/asra_venv` — same bootstrap as Phase 2–4\n\n",
                    "**Submit:** Save & Run All → Submit to competition. Scoring re-runs `my_agent.py`.\n\n",
                    "Agent tag: `asra-v0.7-phase5`",
                ],
            },
            {"cell_type": "markdown", "metadata": {}, "source": ["## 0. Bootstrap venv + competition assets"]},
            {"cell_type": "code", "metadata": {}, "source": [bootstrap_cell], "outputs": [], "execution_count": None},
            {"cell_type": "markdown", "metadata": {}, "source": ["## 1. Write `my_agent.py` (Phase 5)"]},
            {"cell_type": "code", "metadata": {}, "source": [write_agent_cell], "outputs": [], "execution_count": None},
            {"cell_type": "markdown", "metadata": {}, "source": ["## 2. Smoke-test (venv python — simulates scoring)"]},
            {"cell_type": "code", "metadata": {}, "source": [smoke_cell], "outputs": [], "execution_count": None},
            {"cell_type": "markdown", "metadata": {}, "source": ["## 3. Write `submission.parquet` (validation gate)"]},
            {"cell_type": "code", "metadata": {}, "source": [parquet_cell], "outputs": [], "execution_count": None},
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Done\n\n",
                    "Outputs: `my_agent.py` + `submission.parquet`. Do **not** run Swarm in the notebook — Kaggle executes `my_agent.py` during scoring.\n\n",
                    "Spec: `private/phase5/phase5-goal-inference-hypothesis-engine.md`.",
                ],
            },
        ],
    }

    out_path.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    print(f"Wrote {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
