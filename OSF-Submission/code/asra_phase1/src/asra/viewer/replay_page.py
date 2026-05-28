"""Static step-by-step replay from JSONL logs."""

from __future__ import annotations

from pathlib import Path

import streamlit as st

from asra.utils.serialization import read_jsonl
from asra.viewer.grid_viz import render_diff_figure, render_grid_figure, render_side_by_side
from asra.viewer.viewer_ui import show_figure


def render_replay_page() -> None:
    st.subheader("Replay viewer")
    st.caption("Inspect logged transitions: before · after · diff · action · reward · terminal")

    data_dir = Path(st.sidebar.text_input("Data directory", "data", key="replay_data_dir"))
    episode_files = sorted((data_dir / "transitions").glob("*.jsonl"))
    if not episode_files:
        st.info("No episode transition logs found under `data/transitions/`. Try `data` or `data/large_scale`.")
        return

    selected = st.sidebar.selectbox("Episode", episode_files, format_func=lambda path: path.stem, key="replay_episode")
    transitions = read_jsonl(selected)
    if not transitions:
        st.warning("Empty episode.")
        return

    step = st.slider("Step", min_value=0, max_value=len(transitions) - 1, value=0, key="replay_step")
    row = transitions[step]
    diff = row.get("diff", {})
    changed = diff.get("changed_cells", [])
    meta = row.get("metadata", {})

    st.markdown(f"**Episode `{selected.stem}`** — log index {step} · `step_index` {row.get('step_index', '—')}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Action", row["action"]["name"])
    c2.metric("Reward", row["reward"])
    c3.metric("Terminal", row["terminal_state"])
    c4.metric("Status", row["next_state"].get("status", "—"))

    st.write(
        {
            "changed_cells": diff.get("num_changed_cells", 0),
            "change_ratio": diff.get("change_ratio", 0),
            "dead_end_score": meta.get("dead_end_score"),
            "policy": meta.get("policy"),
        }
    )

    show_figure(
        render_side_by_side(
            row["state"]["grid"],
            row["next_state"]["grid"],
            changed,
            action_name=row["action"]["name"],
        )
    )

    with st.expander("Numeric grids & hashes"):
        left, right = st.columns(2)
        left.write("State grid")
        left.dataframe(row["state"]["grid"], hide_index=True)
        right.write("Next state grid")
        right.dataframe(row["next_state"]["grid"], hide_index=True)
        st.code(f"{row['state']['state_hash']}\n  →\n{row['next_state']['state_hash']}")
        st.json(changed)
        st.write("Metadata")
        st.json(meta)

    if st.checkbox("Show per-panel color grids", key="replay_color_panels"):
        p1, p2, p3 = st.columns(3)
        with p1:
            show_figure(render_grid_figure(row["state"]["grid"], title="State"))
        with p2:
            show_figure(render_grid_figure(row["next_state"]["grid"], title="Next state"))
        with p3:
            show_figure(render_diff_figure(row["state"]["grid"], changed, title="Diff overlay"))
