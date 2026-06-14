"""Build ARC-AGI-3 Kaggle notebooks using the official gateway sidecar pattern."""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent

from phase_registry import COMP, PhaseConfig

ACCELERATORS = {
    "cpu": {"name": "none", "gpu": False},
    "t4": {"name": "nvidiaTeslaT4", "gpu": True},
}


def code_cell(source: str) -> dict:
    return {
        "cell_type": "code",
        "metadata": {"trusted": True},
        "outputs": [],
        "execution_count": None,
        "source": source,
    }


def markdown_cell(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def build_notebook(phase: PhaseConfig, agent_body: str, *, accelerator: str = "cpu") -> dict:
    if accelerator not in ACCELERATORS:
        raise ValueError(f"Unknown accelerator {accelerator!r}; choose {sorted(ACCELERATORS)}")
    accel = ACCELERATORS[accelerator]

    install_cell = code_cell(
        "!pip install --no-index --find-links \\\n"
        f" /kaggle/input/competitions/{COMP}/arc_agi_3_wheels \\\n"
        " arc-agi python-dotenv"
    )
    write_agent_cell = code_cell("%%writefile /tmp/my_agent.py\n" + agent_body)
    run_cell = code_cell(
        dedent(
            f"""\
            import os

            if os.getenv('KAGGLE_IS_COMPETITION_RERUN'):
                !curl --fail --retry 999 --retry-all-errors --retry-delay 5 \\
                --retry-max-time 600 http://gateway:8001/api/games

                !cp -r /kaggle/input/competitions/{COMP}/ARC-AGI-3-Agents \\
                /kaggle/working/ARC-AGI-3-Agents

                !cp /tmp/my_agent.py \\
                /kaggle/working/ARC-AGI-3-Agents/agents/templates/my_agent.py

                with open('/kaggle/working/ARC-AGI-3-Agents/agents/__init__.py', 'w') as f:
                    f.write(\"\"\"from typing import Type
            from dotenv import load_dotenv
            from .agent import Agent, Playback
            from .swarm import Swarm
            from .templates.random_agent import Random
            from .templates.my_agent import MyAgent

            load_dotenv()

            AVAILABLE_AGENTS: dict[str, Type[Agent]] = {{
                'random': Random,
                'myagent': MyAgent,
            }}
            \"\"\")

                with open('/kaggle/working/ARC-AGI-3-Agents/.env', 'w') as f:
                    f.write(\"\"\"SCHEME=http
            HOST=gateway
            PORT=8001
            ARC_API_KEY=test-key-123
            ARC_BASE_URL=http://gateway:8001/
            OPERATION_MODE=online
            ENVIRONMENTS_DIR=
            RECORDINGS_DIR=/kaggle/working/server_recording
            \"\"\")

                !cd /kaggle/working/ARC-AGI-3-Agents && \\
                MPLBACKEND=agg \\
                python main.py --agent myagent
            """
        )
    )
    dummy_cell = code_cell(
        dedent(
            """\
            import os
            if not os.getenv('KAGGLE_IS_COMPETITION_RERUN'):
                import pandas as pd
                submission = pd.DataFrame(
                    data=[['1_0', '1', True, 1]],
                    columns=['row_id', 'game_id', 'end_of_game', 'score'])
                submission.to_parquet('/kaggle/working/submission.parquet', index=False)
                submission.head()
            """
        )
    )

    template_name = phase.template_agent.name
    return {
        "metadata": {
            "kernelspec": {
                "language": "python",
                "display_name": "Python 3",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "mimetype": "text/x-python",
                "file_extension": ".py",
                "pygments_lexer": "ipython3",
            },
            "kaggle": {
                "accelerator": accel["name"],
                "isInternetEnabled": False,
                "isGpuEnabled": accel["gpu"],
                "language": "python",
                "sourceType": "notebook",
                "competitionSources": [COMP],
            },
        },
        "nbformat_minor": 4,
        "nbformat": 4,
        "cells": [
            markdown_cell(
                f"# {phase.title}\n\n"
                f"Built from `{template_name}` via `_shared/gateway_notebook.py`. "
                "Official ARC-AGI-3 gateway sidecar + dummy parquet gate.\n\n"
                f"**Agent tag:** `{phase.agent_tag}`"
            ),
            install_cell,
            write_agent_cell,
            run_cell,
            dummy_cell,
        ],
    }


def build_and_write(phase: PhaseConfig, *, accelerator: str = "cpu") -> Path:
    if not phase.template_agent.is_file():
        raise FileNotFoundError(
            f"Template agent missing: {phase.template_agent}\n"
            f"Run: python3 kaggle-notebooks/_shared/extract_template_agent.py --phase {phase.number}"
        )
    body = phase.template_agent.read_text(encoding="utf-8")
    nb = build_notebook(phase, body, accelerator=accelerator)
    phase.notebook_path.write_text(json.dumps(nb, indent=1), encoding="utf-8")
    return phase.notebook_path
