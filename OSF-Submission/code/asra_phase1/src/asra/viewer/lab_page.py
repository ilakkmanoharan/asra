"""Human-playable mock environment (ASRA Lab)."""

from __future__ import annotations

import streamlit as st

from asra.analysis.grid_diff import diff_grid
from asra.env.action_space import SUPPORTED_ACTIONS
from asra.env.arc_agi3_runner import MockArcAGI3Environment
from asra.env.frame_parser import parse_frame
from asra.utils.hashing import hash_state
from asra.viewer.grid_viz import render_grid_figure, render_side_by_side
from asra.viewer.viewer_ui import action_target_label, show_figure


def _init_lab() -> None:
    if "lab_env" not in st.session_state:
        _apply_scenario("default")


def _apply_scenario(scenario: str) -> None:
    st.session_state.lab_scenario = scenario
    st.session_state.lab_env = MockArcAGI3Environment(scenario=scenario)
    st.session_state.lab_moves = 0
    st.session_state.lab_last = None
    raw = st.session_state.lab_env.reset("lab-game", "lab-level")
    st.session_state.lab_status = parse_frame(raw).status


def _do_action(action: str) -> None:
    env: MockArcAGI3Environment = st.session_state.lab_env
    before = [row[:] for row in env.grid]
    before_hash = hash_state(before)
    raw = env.step(action)
    after = [row[:] for row in env.grid]
    frame = parse_frame(raw)
    diff = diff_grid(before, after)
    st.session_state.lab_moves += 1
    st.session_state.lab_status = frame.status
    st.session_state.lab_last = {
        "action": action,
        "before": before,
        "after": after,
        "before_hash": before_hash,
        "after_hash": hash_state(after),
        "diff": diff,
        "status": frame.status,
        "reward": float(raw.get("reward", 0.0)),
        "terminal": frame.status in {"WIN", "GAME_OVER"},
        "target": action_target_label(action),
    }


def render_lab_page() -> None:
    st.subheader("ASRA Lab — playable mock")
    st.caption("Same rules as `MockArcAGI3Environment`: each ACTION cycles one cell’s color; RESET restores the start grid.")

    _init_lab()

    scenario = st.selectbox(
        "Scenario",
        ["default", "terminal_demo", "game_over_demo"],
        index=["default", "terminal_demo", "game_over_demo"].index(st.session_state.lab_scenario),
        key="lab_scenario_select",
        help="terminal_demo → WIN after a few steps; game_over_demo → GAME_OVER",
    )
    if scenario != st.session_state.lab_scenario:
        _apply_scenario(scenario)

    env: MockArcAGI3Environment = st.session_state.lab_env

    col_grid, col_help = st.columns([1, 1])
    with col_help:
        st.markdown(
            """
**Color cycle** (per cell): `0` black → `1` blue → `2` red → `3` green → `0` …

**Start grid:** center cell is blue (`1`), rest black.

| Action | Affects |
|--------|---------|
| `ACTION1` | top-left `(0,0)` |
| `ACTION2` | top-center `(1,0)` |
| `ACTION3` | top-right `(2,0)` |
| `ACTION4` | middle-left `(0,1)` |
| `ACTION5` | center `(1,1)` |
| `ACTION6` | middle-right `(2,1)` |
| `ACTION7` | bottom-left `(0,2)` |
| `RESET` | full grid → start |
"""
        )
        st.metric("Moves", st.session_state.lab_moves)
        if st.button("New game (reset environment)", type="primary"):
            _apply_scenario(st.session_state.lab_scenario)

    with col_grid:
        st.markdown("**Current grid**")
        status = st.session_state.get("lab_status", "NOT_FINISHED")
        show_figure(render_grid_figure(env.grid, title=f"Step {env.step_index} · {status}"))

    st.markdown("**Take an action**")
    btn_cols = st.columns(4)
    for i, action in enumerate(SUPPORTED_ACTIONS):
        label = action if action == "RESET" else f"{action}\n{action_target_label(action)}"
        if btn_cols[i % 4].button(label, key=f"lab_btn_{action}", use_container_width=True):
            _do_action(action)
            st.rerun()

    last = st.session_state.lab_last
    if last:
        st.markdown("---")
        st.markdown(f"**Last move:** `{last['action']}` → {last['target']}")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Reward", last["reward"])
        m2.metric("Status", last["status"])
        m3.metric("Terminal", last["terminal"])
        m4.metric("Changed cells", last["diff"]["num_changed_cells"])

        show_figure(
            render_side_by_side(
                last["before"],
                last["after"],
                last["diff"]["changed_cells"],
                action_name=last["action"],
            )
        )
        st.code(f"{last['before_hash']}\n  →\n{last['after_hash']}")
        with st.expander("Diff JSON (what ASRA logs)"):
            st.json(last["diff"])
