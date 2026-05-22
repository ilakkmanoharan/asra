"""Auto-advance replay animation from JSONL logs."""

from __future__ import annotations

import time
from pathlib import Path

import streamlit as st

from asra.utils.serialization import read_jsonl
from asra.viewer.grid_viz import render_side_by_side
from asra.viewer.viewer_ui import show_figure


def _reset_animation() -> None:
    st.session_state.anim_playing = False
    st.session_state.anim_step = 0


def render_animated_replay_page() -> None:
    st.subheader("Animated replay")
    st.caption("Auto-play logged transitions step-by-step (same panels as Replay viewer).")

    if "anim_playing" not in st.session_state:
        _reset_animation()

    data_dir = Path(st.sidebar.text_input("Data directory", "data", key="anim_data_dir"))
    episode_files = sorted((data_dir / "transitions").glob("*.jsonl"))
    if not episode_files:
        st.info("No episodes under `data/transitions/`.")
        return

    selected = st.sidebar.selectbox("Episode", episode_files, format_func=lambda p: p.stem, key="anim_episode")
    transitions = read_jsonl(selected)
    if not transitions:
        st.warning("Empty episode.")
        return

    interval_ms = st.sidebar.slider("Frame interval (ms)", 100, 2000, 300, 50, key="anim_interval")
    max_step = len(transitions) - 1

    ctrl1, ctrl2, ctrl3, ctrl4 = st.columns(4)
    if ctrl1.button("Play", type="primary"):
        st.session_state.anim_playing = True
        st.session_state.anim_step = st.session_state.get("anim_step", 0)
    if ctrl2.button("Pause"):
        st.session_state.anim_playing = False
    if ctrl3.button("Stop"):
        _reset_animation()
    if ctrl4.button("Step back"):
        st.session_state.anim_playing = False
        st.session_state.anim_step = max(0, st.session_state.get("anim_step", 0) - 1)

    manual_step = st.slider(
        "Frame",
        0,
        max_step,
        st.session_state.get("anim_step", 0),
        key="anim_manual_step",
        disabled=st.session_state.anim_playing,
    )
    if not st.session_state.anim_playing:
        st.session_state.anim_step = manual_step

    step = st.session_state.anim_step
    row = transitions[step]
    diff = row.get("diff", {})
    changed = diff.get("changed_cells", [])

    st.progress((step + 1) / len(transitions), text=f"Frame {step + 1} / {len(transitions)}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Action", row["action"]["name"])
    c2.metric("Reward", row["reward"])
    c3.metric("Terminal", row["terminal_state"])
    c4.metric("Changed", diff.get("num_changed_cells", 0))

    show_figure(
        render_side_by_side(
            row["state"]["grid"],
            row["next_state"]["grid"],
            changed,
            action_name=row["action"]["name"],
        )
    )

    if st.session_state.anim_playing:
        if step < max_step:
            time.sleep(interval_ms / 1000.0)
            st.session_state.anim_step = step + 1
            st.rerun()
        else:
            st.session_state.anim_playing = False
            st.success("Playback finished.")
