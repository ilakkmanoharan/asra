from __future__ import annotations

from pathlib import Path

import streamlit as st

from asra.utils.serialization import read_jsonl

st.set_page_config(page_title="ASRA Replay Viewer", layout="wide")
st.title("ASRA v0.1 Replay Viewer")

data_dir = Path(st.sidebar.text_input("Data directory", "data"))
episode_files = sorted((data_dir / "transitions").glob("*.jsonl"))
if not episode_files:
    st.info("No episode transition logs found.")
    st.stop()

selected = st.sidebar.selectbox("Episode", episode_files, format_func=lambda path: path.stem)
transitions = read_jsonl(selected)
step = st.slider("Step", min_value=0, max_value=max(len(transitions) - 1, 0), value=0)
row = transitions[step]

st.subheader(f"Episode {selected.stem} / Step {row['step_index']}")
st.write({"action": row["action"], "reward": row["reward"], "terminal_state": row["terminal_state"], "status": row["next_state"]["status"]})
left, right, diff = st.columns(3)
left.write("State")
left.dataframe(row["state"]["grid"], hide_index=True)
right.write("Next State")
right.dataframe(row["next_state"]["grid"], hide_index=True)
diff.write("Changed Cells")
diff.json(row.get("diff", {}).get("changed_cells", []))
st.write("Metadata")
st.json(row.get("metadata", {}))
st.write("State hashes")
st.code(f"{row['state']['state_hash']} -> {row['next_state']['state_hash']}")
