"""Shared Streamlit viewer helpers."""

from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st

from asra.env.action_space import SUPPORTED_ACTIONS


def show_figure(fig: plt.Figure) -> None:
    st.pyplot(fig)
    plt.close(fig)


def action_target_cell(action: str) -> tuple[int, int] | None:
    """Cell (x, y) affected by ACTION1..ACTION7 in MockArcAGI3Environment."""
    if action not in SUPPORTED_ACTIONS[1:]:
        return None
    idx = SUPPORTED_ACTIONS.index(action) - 1
    return idx % 3, idx // 3


def action_target_label(action: str) -> str:
    cell = action_target_cell(action)
    if cell is None:
        return "whole grid"
    x, y = cell
    return f"cell ({x}, {y})"
