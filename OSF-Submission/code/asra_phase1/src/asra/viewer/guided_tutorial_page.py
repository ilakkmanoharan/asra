"""Guided slow replay: first 10 log frames with formulas and next-step explanations."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import streamlit as st

from asra.utils.serialization import read_jsonl
from asra.viewer.grid_viz import render_grid_figure, render_side_by_side
from asra.viewer.mock_rules import (
    action_formula_markdown,
    action_semantic_label,
    apply_mock_action,
    explain_transition,
    movement_description,
    preview_next_step_markdown,
)
from asra.viewer.viewer_ui import show_figure

MAX_FRAMES = 10
DEFAULT_EPISODE = "5830e744-ad91-4cbb-93be-f38949366c7e"


def _init_guided() -> None:
    st.session_state.setdefault("guided_idx", 0)
    st.session_state.setdefault("guided_auto", False)
    st.session_state.setdefault("guided_started", False)


def render_guided_tutorial_page() -> None:
    st.subheader("Guided tutorial — first 10 frames (slow)")
    st.caption(
        "Pauses on each logged transition. Shows the **action formula**, what happened, "
        "and **what the next frame will do** before you advance."
    )

    _init_guided()

    data_dir = Path(st.sidebar.text_input("Data directory", "data", key="guided_data_dir"))
    episode_files = sorted((data_dir / "transitions").glob("*.jsonl"))
    if not episode_files:
        st.info("No episodes under `data/transitions/`.")
        return

    default_ix = 0
    stems = [p.stem for p in episode_files]
    if DEFAULT_EPISODE in stems:
        default_ix = stems.index(DEFAULT_EPISODE)

    selected = st.sidebar.selectbox(
        "Episode",
        episode_files,
        index=default_ix,
        format_func=lambda p: p.stem,
        key="guided_episode",
    )
    transitions = read_jsonl(selected)[:MAX_FRAMES]
    if not transitions:
        st.warning("Episode empty.")
        return

    pause_sec = st.sidebar.slider(
        "Auto-advance pause (seconds)",
        min_value=2.0,
        max_value=15.0,
        value=5.0,
        step=0.5,
        key="guided_pause",
        help="Longer pause = more time to read before the next frame.",
    )
    st.sidebar.checkbox("Auto-advance (slow)", key="guided_auto")

    if st.sidebar.button("Restart tutorial", type="secondary"):
        st.session_state.guided_idx = 0
        st.session_state.guided_started = True
        st.session_state.guided_auto = False
        st.rerun()

    idx = min(st.session_state.guided_idx, len(transitions) - 1)
    row = transitions[idx]
    nxt = transitions[idx + 1] if idx + 1 < len(transitions) else None

    st.progress((idx + 1) / len(transitions), text=f"Frame {idx + 1} of {len(transitions)} (log lines 0–9)")

    c_prev, c_next, c_play = st.columns([1, 1, 2])
    if c_prev.button("◀ Previous", disabled=idx <= 0):
        st.session_state.guided_idx = max(0, idx - 1)
        st.session_state.guided_auto = False
        st.rerun()
    if c_next.button("Next ▶", disabled=idx >= len(transitions) - 1):
        st.session_state.guided_idx = min(len(transitions) - 1, idx + 1)
        st.session_state.guided_auto = False
        st.rerun()
    if c_play.button("Start / resume from frame 1", type="primary"):
        st.session_state.guided_started = True
        st.rerun()

    action = row["action"]["name"]
    state_grid = row["state"]["grid"]
    next_grid = row["next_state"]["grid"]
    changed = row.get("diff", {}).get("changed_cells", [])

    left, right = st.columns([1, 1])

    with left:
        st.markdown("### This frame — what happened")
        st.markdown(f"## ACTION = {action_semantic_label(action)}")
        st.info(movement_description(changed))
        st.markdown(f"**Log index `{idx}`** · logged action **`{action}`**")
        with st.expander("Action definition (mock formula)", expanded=True):
            st.markdown(action_formula_markdown(action))
        st.markdown(explain_transition(row))

        st.markdown("**Before → After → Changed**")
        show_figure(
            render_side_by_side(state_grid, next_grid, changed, action_name=action),
        )

    with right:
        st.markdown("### Predicted vs logged (sanity check)")
        predicted = apply_mock_action(state_grid, action)
        match = predicted == next_grid
        st.markdown(
            "Mock formula applied to **before** grid: "
            + ("**matches** logged after grid." if match else "**differs** from logged after (non-mock or extra logic).")
        )
        p1, p2 = st.columns(2)
        with p1:
            show_figure(render_grid_figure(state_grid, title="Before (this frame)"))
        with p2:
            show_figure(render_grid_figure(predicted, title="Formula prediction"))

        st.markdown("---")
        st.markdown(preview_next_step_markdown(row, nxt, idx))

    with st.expander("Raw transition JSON (this frame)"):
        st.json(row)

    if idx >= len(transitions) - 1:
        st.success("Tutorial complete for the first 10 frames. Use **Replay** or **Animated replay** for the full episode.")
        st.session_state.guided_auto = False
    elif st.session_state.guided_auto:
        st.info(f"Auto-advance in **{pause_sec:.1f}s** — read the panels above, then the next frame loads.")
        time.sleep(pause_sec)
        st.session_state.guided_idx = idx + 1
        st.rerun()
