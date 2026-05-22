"""ASRA Phase 1 viewer: replay, playable lab, animated replay."""

from __future__ import annotations

import streamlit as st

from asra.viewer.animated_replay_page import render_animated_replay_page
from asra.viewer.guided_tutorial_page import render_guided_tutorial_page
from asra.viewer.lab_page import render_lab_page
from asra.viewer.replay_page import render_replay_page

st.set_page_config(page_title="ASRA Viewer", layout="wide", initial_sidebar_state="expanded")
st.title("ASRA v0.1 Viewer")
st.caption("Phase 1 tools: inspect logs · play the mock world · animate episodes")

tab_replay, tab_lab, tab_anim, tab_guided = st.tabs(
    ["Replay (step-by-step)", "ASRA Lab (play)", "Animated replay", "Guided tutorial (10 steps)"]
)

with tab_replay:
    render_replay_page()

with tab_lab:
    render_lab_page()

with tab_anim:
    render_animated_replay_page()

with tab_guided:
    render_guided_tutorial_page()
