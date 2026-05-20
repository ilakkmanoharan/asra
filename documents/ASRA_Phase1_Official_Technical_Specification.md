# ASRA Phase 1 — Official Technical Specification & System Documentation

## Project

**ASRA — Adaptive Scientific Reasoning Architecture**

Phase 1 focuses on building the foundational interaction, observation, experimentation, and memory infrastructure required for adaptive intelligence in unseen environments.

**Video overview:** [ASRA Phase 1 — Adaptive Experimental Memory](https://youtu.be/Jyak9_ev8h0)

---

# 1. Executive Summary

ASRA Phase 1 establishes the first operational layer of the architecture:

```text
Environment Interaction + Experimental Memory Formation
```

The system interacts with ARC-AGI-3 environments, performs exploratory actions, observes environmental reactions, computes state differences, records transitions, constructs state graphs, detects dead-ends, and exports structured experience datasets.

The primary outcome of this phase is not task-solving performance.

The primary outcome is:

```text
A reproducible interaction-to-knowledge pipeline.
```

This phase transforms ASRA from a static reasoning concept into a functioning interactive experimental system.

---

# 2. Core Philosophy

Traditional AI systems are often optimized for:

* memorization,
* static benchmark performance,
* supervised pattern matching,
* fixed action semantics,
* known environments.

ASRA instead treats intelligence as:

```text
adaptive experimentation in unknown environments
```

The architecture assumes:

* action meanings are unknown,
* environments are partially understood,
* interaction must precede reasoning,
* knowledge emerges from experimentation,
* memory must be constructed through observation.

Phase 1 operationalizes this philosophy.

---

# 3. Primary Goal of Phase 1

The goal of Phase 1 is:

```text
Build the scientific observation and experimental memory infrastructure of ASRA.
```

This includes:

* environment interaction,
* frame parsing,
* action experimentation,
* state transition logging,
* replay infrastructure,
* state graph construction,
* exploratory behavior,
* dead-end detection,
* dataset generation.

---

# 4. Non-Goals of Phase 1

Phase 1 is NOT focused on:

* solving ARC tasks optimally,
* symbolic abstraction,
* planning,
* strategy invention,
* world-model learning,
* reasoning over latent concepts,
* long-horizon intelligence.

Those emerge in later phases.

---

# 5. Phase 1 System Architecture

```text
ARC-AGI-3 Environment
        ↓
Environment Runner
        ↓
Frame Parser
        ↓
Exploration Policy
        ↓
Action Execution
        ↓
State Transition
        ↓
Grid Differencing
        ↓
State Hashing
        ↓
Transition Logging
        ↓
State Graph Construction
        ↓
Replay + Dataset Export
```

---

# 6. Core Components

## 6.1 ARC-AGI-3 Runner

### Purpose

Provides a standardized interaction interface with ARC-AGI-3 environments.

### Responsibilities

* reset environments,
* receive frames,
* send actions,
* receive next states,
* track terminal conditions.

### Supported Actions

```text
RESET
ACTION1
ACTION2
ACTION3
ACTION4
ACTION5
ACTION6
ACTION7
```

### Important Principle

ASRA does NOT assume predefined action semantics.

Actions are treated as unknown experimental operators.

---

## 6.2 Frame Parser

### Purpose

Convert raw ARC-AGI-3 frames into normalized internal representations.

### Input

Raw environment JSON frame.

### Output

```json
{
  "grid": [[0,1,2]],
  "height": 1,
  "width": 3,
  "status": "NOT_FINISHED"
}
```

### Validation Rules

* rectangular grids only,
* max size 64×64,
* integer cell values 0–15,
* valid status fields,
* top-left coordinate origin.

---

## 6.3 Grid Differencing Engine

### Purpose

Measure visible environmental change caused by actions.

### Input

```text
state grid
next_state grid
```

### Output

```json
{
  "changed_cells": [],
  "num_changed_cells": 0,
  "change_ratio": 0.0
}
```

### Importance

Grid differencing enables:

* action-effect analysis,
* novelty estimation,
* exploration scoring,
* semantic inference,
* transition analysis.

---

## 6.4 State Hashing

### Purpose

Provide deterministic identity for states.

### Requirements

Same grid:

```text
must always produce same hash
```

Different grids:

```text
must produce different hashes
```

### Importance

Hashing enables:

* memory,
* replay,
* graph construction,
* cycle detection,
* transition lookup,
* planning,
* world modeling.

Without stable hashing:

```text
memory infrastructure collapses
```

---

## 6.5 Episode Logger

### Purpose

Persist all interactions as structured experimental records.

### Core Transition Structure

```text
state
→ action
→ next_state
→ reward
→ terminal_state
→ metadata
```

### Importance

This becomes ASRA’s first experiential memory system.

---

## 6.6 Exploration Policy

### Purpose

Drive exploratory interaction behavior.

### Initial Policy

```text
simple_exploration
```

### Behavior

* prefer novel states,
* avoid loops,
* test untried actions,
* detect dead-ends,
* occasionally reset,
* maximize environmental coverage.

---

## 6.7 Dead-End Detector

### Purpose

Detect non-productive regions of the environment.

### Indicators

* repeated states,
* no grid changes,
* cyclic transitions,
* GAME_OVER states,
* exhausted actions.

### Importance

Prevents wasted exploration.

---

## 6.8 State Graph

### Purpose

Construct a graph of environmental dynamics.

### Representation

```text
Node = state
Edge = action transition
```

### Importance

Creates ASRA’s first environmental topology model.

---

## 6.9 Replay Viewer

### Purpose

Enable visual inspection of agent behavior.

### Visualizations

* before-state grid,
* after-state grid,
* action taken,
* changed cells,
* reward,
* terminal status,
* state transitions.

### Importance

ARC environments are visual.

Understanding requires replay visualization.

---

# 7. Input Data

## Primary Dataset

ARC-AGI-3 Interactive Environments

### Environment Characteristics

* unseen tasks,
* hidden mechanics,
* sparse information,
* unknown action semantics,
* interactive exploration,
* dynamic state transitions.

---

# 8. Output Files

---

# 8.1 Transition Dataset

## File

```text
data/exports/asra_v0_1_transitions.jsonl
```

## Purpose

Stores all experimental transitions.

## Structure

```text
state
→ action
→ next_state
→ reward
→ terminal_state
→ metadata
```

## What Can Be Inferred

```text
- action effects
- novelty patterns
- repeated transitions
- environment dynamics
- local causality
- exploration coverage
- action consistency
- interaction statistics
```

## Importance

This is the most important Phase 1 output.

It becomes the foundation for:

* semantics learning,
* world models,
* planning,
* adaptive reasoning,
* abstraction learning.

---

# 8.2 Parquet Dataset

## File

```text
data/exports/asra_v0_1_transitions.parquet
```

## Purpose

Efficient analytics and ML ingestion.

## Importance

Optimized for:

* pandas,
* PyTorch,
* distributed training,
* large-scale analytics.

---

# 8.3 Episode Summary

## File

```text
data/exports/asra_v0_1_episode_summary.csv
```

## Contains

```text
- steps
- unique states
- cycles
- dead-ends
- rewards
- terminal outcomes
```

## What Can Be Inferred

```text
- exploration efficiency
- loop frequency
- environment coverage
- policy quality
- novelty progression
```

---

# 8.4 State Graph

## File

```text
data/graphs/state_graph.json
```

## Purpose

Store transition topology.

## What Can Be Inferred

```text
- state connectivity
- dangerous states
- exploration hubs
- repeated cycles
- useful action paths
- terminal trajectories
```

---

# 8.5 GraphML Export

## File

```text
data/graphs/state_graph.graphml
```

## Usage

Visual graph analysis tools:

* Gephi,
* Cytoscape,
* NetworkX.

---

# 8.6 Replay Viewer

## File

```text
src/asra/viewer/streamlit_app.py
```

## Run

```bash
streamlit run src/asra/viewer/streamlit_app.py
```

## Visual Features

```text
- episode selector
- step slider
- before/after grids
- diff overlays
- transition metadata
- rewards
- terminal states
```

---

# 9. What Was Accomplished in Phase 1

Phase 1 successfully establishes:

```text
✓ interactive environment execution
✓ structured experimentation
✓ state transition recording
✓ environmental observation
✓ visual differencing
✓ deterministic state identity
✓ graph-based memory
✓ replay infrastructure
✓ exploratory behavior
✓ dataset generation
```

Most importantly:

```text
ASRA now possesses experiential memory.
```

---

# 10. Key Scientific Achievement

The major conceptual breakthrough of Phase 1 is:

```text
ASRA no longer passively predicts.

ASRA experimentally interacts with environments.
```

This transforms the architecture from:

```text
static benchmark intelligence
```

into:

```text
interactive adaptive intelligence
```

---

# 11. What Can Be Learned From Phase 1 Data

The generated datasets enable future learning of:

---

## 11.1 Action Semantics

Example:

```text
ACTION3 usually changes neighboring cells.
ACTION2 often causes GAME_OVER.
ACTION5 creates large state changes.
```

---

## 11.2 Environmental Dynamics

Example:

```text
Certain states act as hubs.
Some trajectories repeatedly terminate.
Some regions are cyclic.
```

---

## 11.3 Novelty Estimation

Example:

```text
Which actions maximize discovery?
Which actions produce no information gain?
```

---

## 11.4 Experimental Efficiency

Example:

```text
How quickly can ASRA map unknown environments?
```

---

# 12. Replay & Visualization Infrastructure

Phase 1 includes visual introspection capabilities.

This is critical because ARC environments are inherently visual.

The replay viewer allows inspection of:

```text
state
→ action
→ next_state
```

step-by-step.

This enables:

* debugging,
* semantic discovery,
* action interpretation,
* policy analysis,
* transition inspection.

---

# 13. Why Stable Hashing Is Critical

Stable hashing is one of the most important Phase 1 validations.

Requirement:

```text
same grid → same hash
```

Without this:

```text
- replay breaks
- graph construction breaks
- memory breaks
- cycle detection breaks
- planning breaks
```

Phase 1 therefore validates the integrity of ASRA’s memory identity system.

---

# 14. Metrics to Evaluate Phase 1

## Key Metrics

```text
- total transitions
- unique states
- transition diversity
- exploration coverage
- cycles detected
- dead-ends detected
- state reuse
- action novelty
- graph connectivity
```

---

# 15. What Success Looks Like

Phase 1 is considered successful if:

```text
✓ ASRA can interact with environments
✓ transitions are logged correctly
✓ state hashes are stable
✓ replay works
✓ graphs build correctly
✓ datasets export successfully
✓ dead-ends are detected
✓ exploration occurs
✓ visual diffs are computed
```

---

# 16. Relationship to Later Phases

Phase 1 creates the foundation for all future ASRA intelligence.

---

## Phase 2

```text
Action Semantics Inference
```

Learn meanings of actions from transition statistics.

---

## Phase 3

```text
World Model Learning
```

Predict environmental dynamics.

---

## Phase 4

```text
Adaptive Strategy Invention
```

Create novel solutions in unseen tasks.

---

## Phase 5

```text
Scientific Reasoning & Abstraction
```

Generalize across environments and domains.

---

# 17. Core Conceptual Shift

Traditional AI:

```text
train → predict
```

ASRA:

```text
observe → experiment → compare → remember → infer
```

Phase 1 operationalizes this shift.

---

# 18. Final Outcome of Phase 1

The final deliverable of Phase 1 is not merely software.

It is:

```text
A reproducible experimental intelligence infrastructure.
```

ASRA can now:

```text
- interact
- observe
- compare
- remember
- replay
- graph
- export
```

This marks the emergence of:

```text
ASRA Experience Engine v0
```

the foundational memory and experimentation layer upon which adaptive scientific reasoning will later emerge.
