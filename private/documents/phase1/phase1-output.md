In Phase 1, you should look for **evidence that ASRA can observe, act, remember, and explain what happened**.

The most important output is not “winning.” The most important output is:

```text
state → action → next_state → reward → terminal_state → metadata
```

## Files to check

```text
File / Folder                                  What you will find                          Why it matters

data/transitions/*.jsonl                       Every action the agent took                  This is your core ASRA learning dataset

data/episodes/*.json                           Full episode history                         Shows complete journey from reset to terminal/end

data/exports/asra_v0_1_transitions.jsonl       Final exported transition dataset            Used later for learning action effects and world dynamics

data/exports/asra_v0_1_transitions.parquet     Same dataset in analytics-friendly format    Useful for notebooks, pandas, ML pipelines

data/exports/asra_v0_1_episode_summary.csv     Episode-level summary                        Tells whether exploration is improving

data/graphs/state_graph.json                   State-action transition graph                 Shows how states connect through actions

data/graphs/state_graph.graphml                Visual graph format if generated             Can open in Gephi/Cytoscape

src/asra/viewer/streamlit_app.py               Replay viewer app                            Lets you visually inspect agent behavior

notebooks/02_analyze_agent_dataset.ipynb       Analysis notebook                            Helps inspect patterns, actions, rewards, dead ends
```

## 1. First check: transition dataset

Open:

```text
data/exports/asra_v0_1_transitions.jsonl
```

You should see rows like:

```json
{
  "episode_id": "ep_001",
  "game_id": "arc_game_x",
  "level_id": "level_1",
  "step_index": 12,
  "state": {
    "grid": [[0,0,1],[0,2,1]],
    "state_hash": "abc123"
  },
  "action": {
    "name": "ACTION3"
  },
  "next_state": {
    "grid": [[0,0,1],[0,0,2]],
    "state_hash": "def456"
  },
  "reward": 0.0,
  "terminal_state": false,
  "diff": {
    "num_changed_cells": 2,
    "change_ratio": 0.33
  },
  "metadata": {
    "policy": "simple_exploration",
    "agent_version": "asra-v0.1"
  }
}
```

What you can infer:

```text
Question                                      Answer from this file

Did the agent interact correctly?             Yes, if transitions are being logged.

Did actions change the grid?                  Check diff.num_changed_cells.

Which actions do something useful?            Group by action.name and compare changes.

Which actions cause no change?                Look for num_changed_cells = 0.

Which actions lead to terminal states?        Check terminal_state = true.

Is the agent exploring or cycling?            Compare state_hash and next_state_hash.

Is there enough data for Phase 2?             Check number and diversity of transitions.
```

Why it is useful:

This is the **raw experience memory** of ASRA. Later phases can learn action semantics, causality, planning, and strategy from this file.

## 2. Check episode summaries

Open:

```text
data/exports/asra_v0_1_episode_summary.csv
```

You should see something like:

```text
episode_id,game_id,level_id,num_steps,unique_states,num_cycles,num_dead_ends,final_status,total_reward
ep_001,game_a,level_1,120,38,12,4,NOT_FINISHED,0.0
ep_002,game_a,level_1,87,44,6,2,WIN,1.0
ep_003,game_b,level_1,200,29,41,9,GAME_OVER,-1.0
```

What to look for:

```text
Metric                         Good sign                         Warning sign

unique_states                  Increasing over time               Very low unique states

num_cycles                     Decreasing over time               Agent loops repeatedly

num_dead_ends                  Low or decreasing                   Agent gets stuck often

final_status                   Some WIN outcomes eventually       Always GAME_OVER

num_steps                      Enough exploration                  Ends too quickly

total_reward                   Improves over episodes             Always zero or negative
```

Why it is useful:

This tells you whether ASRA is becoming a better explorer.

## 3. Check state graph

Open:

```text
data/graphs/state_graph.json
```

You will find:

```json
{
  "nodes": {
    "state_hash_1": {
      "visit_count": 4,
      "terminal": false
    }
  },
  "edges": [
    {
      "from": "state_hash_1",
      "to": "state_hash_2",
      "action": "ACTION2",
      "count": 3,
      "avg_reward": 0.0
    }
  ]
}
```

What you can infer:

```text
Graph pattern                         Meaning

Many nodes                            Agent is exploring many states

Few nodes, many repeated edges         Agent is stuck in loops

Edges leading to WIN                  Useful action paths

Edges leading to GAME_OVER            Dangerous action paths

High visit_count nodes                Common or repeated states

One action creates many new states     That action may be important
```

Why it is useful:

This is ASRA’s first **world map**.

It tells you:

```text
where the agent has been
which actions move it forward
which paths loop
which states are dangerous
which states are promising
```

## 4. Check replay viewer app

Yes — you should have an app.

Run:

```bash
streamlit run src/asra/viewer/streamlit_app.py
```

The replay viewer should show:

```text
Visual / Panel                         What it shows

Episode selector                       Choose which run to inspect

Step slider                            Move through the episode step-by-step

State grid                             What the agent saw before action

Next-state grid                        What happened after action

Diff grid                              Which cells changed

Action taken                           ACTION1 / ACTION2 / etc.

Reward                                 Whether action helped

Terminal status                        NOT_FINISHED / WIN / GAME_OVER

State hash                             Identity of current state

Next state hash                        Identity of resulting state
```

This is very important because ARC is visual. You need to **see** whether the agent is doing meaningful exploration.

## 5. Check grid diffs

Inside each transition, inspect:

```json
"diff": {
  "changed_cells": [
    {"x": 2, "y": 1, "from": 0, "to": 3}
  ],
  "num_changed_cells": 1,
  "change_ratio": 0.04
}
```

What you can infer:

```text
Diff result                     Meaning

0 changed cells                 Action did nothing or failed

Small localized change           Movement, toggle, object update, local interaction

Large change                     Reset, transformation, level event, major environment reaction

Repeated same diff               Action has stable semantics

Different diff each time         Action may depend on state/context
```

Why it is useful:

Grid diff is the first step toward **action semantics inference**.

## 6. Check dead-end reports

You should find dead-end metadata inside logs or summaries.

Example:

```json
{
  "state_hash": "abc123",
  "dead_end_score": 0.85,
  "reasons": [
    "cycle_detected",
    "no_grid_change",
    "all_actions_tested"
  ],
  "recommended_action": "RESET"
}
```

What you can infer:

```text
Dead-end reason               Meaning

no_grid_change                Actions are not affecting environment

cycle_detected                Agent is moving in circles

all_actions_tested            No obvious action works from this state

GAME_OVER                     Bad terminal path

recommended RESET             Agent should restart exploration
```

Why it is useful:

This prevents ASRA from wasting time.

## 7. What a good Phase 1 output looks like

A good Phase 1 run should produce:

```text
Output                                      Good sign

Transitions                                 Hundreds or thousands of rows

Episode summaries                           Multiple episodes completed

State graph                                 Many connected states

Replay viewer                               Can inspect every step visually

Grid diffs                                  Clear action effects

Dead-end detector                           Identifies loops and stuck states

Dataset export                              JSONL + Parquet successfully generated
```

## 8. What you should conclude from Phase 1

At the end of Phase 1, you should be able to say:

```text
ASRA can now interact with ARC-AGI-3 environments.

It can observe frames.

It can take actions.

It can record state-action-next-state transitions.

It can detect visual changes.

It can build a graph of environment dynamics.

It can replay its own behavior.

It can export a dataset generated by its own exploration.
```

The key achievement is:

```text
ASRA now has experience memory.
```

That memory becomes the foundation for Phase 2:

```text
action semantics inference
```

and later:

```text
world modeling
planning
strategy invention
scientific reasoning
```

So Phase 1 is successful when you can **open the logs, replay the episode, inspect the graph, and understand what the agent experienced**.
