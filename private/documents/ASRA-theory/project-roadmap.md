Below is the **ASRA project roadmap** for ARC Prize 2026 / ARC-AGI-3.

ARC-AGI-3 rewards agents that can explore unknown environments, infer hidden goals, build internal models, and act efficiently without instructions. Key competition dates: **Milestone #1: June 30, 2026**, **Milestone #2: September 30, 2026**, **final submissions: November 2, 2026**. ([ARC Prize][1])

```text
PHASE 1 — Build the Working Baseline
Timeline: Now → June 30, 2026
Goal: Submit a functional ASRA agent for Milestone #1

Milestone 1.1 — Environment Runner
- Set up ARC-AGI-3 SDK / Kaggle workflow
- Load games, frames, actions, rewards, terminal states
- Save every episode as structured logs
- Build replay viewer or simple dashboard

Milestone 1.2 — State Representation
- Convert grid frames into objects, regions, colors, positions, changes
- Track before/after differences after each action
- Store transitions: state → action → next state
- Detect repeated states and dead ends

Milestone 1.3 — Exploration Baseline
- Start with systematic action testing
- Try each action in each new state
- Avoid repeated useless action loops
- Build a graph of explored states and transitions

Milestone 1.4 — First Submission
- Submit a simple agent that can explore and solve easy levels
- Measure score, failure cases, action efficiency
```

A strong baseline should not start with a giant model. It should start with **structured exploration**, because graph-based state tracking has already shown strong results on ARC-AGI-3-style interactive tasks compared with pure LLM agents. ([arXiv][2])

```text
PHASE 2 — Add ASRA Core Intelligence
Timeline: July → August 2026
Goal: Move from exploration to hypothesis-driven reasoning

Milestone 2.1 — Action Semantics Inference
- Infer what ACTION1–ACTION5 do from observed changes
- Examples:
  - moves object
  - rotates object
  - paints cell
  - pushes block
  - toggles state
  - collects item
  - opens path
- Create action-effect summaries per game

Milestone 2.2 — Goal Inference
- Detect what improves the state
- Look for signals:
  - object reaches target
  - color alignment improves
  - obstacles disappear
  - score/progress changes
  - terminal WIN states
- Build possible goal hypotheses

Milestone 2.3 — Hypothesis Engine
- Generate candidate rules:
  - “red object must reach blue cell”
  - “match pattern”
  - “remove all obstacles”
  - “collect all tokens”
  - “avoid dangerous cells”
- Test hypotheses through small action experiments
- Keep, revise, or discard hypotheses

Milestone 2.4 — Memory Across Levels
- Carry learned mechanics from Level 1 to harder levels
- Store:
  - action meanings
  - object roles
  - goal patterns
  - successful strategies
- Reuse strategies when a new level looks structurally similar
```

```text
PHASE 3 — Planning and Strategy Invention
Timeline: August → September 30, 2026
Goal: Submit a much stronger ASRA agent for Milestone #2

Milestone 3.1 — Planner
- Use BFS/A*/graph search when action effects are known
- Use Monte Carlo search when effects are uncertain
- Use short-horizon planning first, then expand
- Prefer efficient paths, not random action spam

Milestone 3.2 — Strategy Library
- Create reusable strategy templates:
  - reach target
  - collect objects
  - align shapes
  - transform pattern
  - avoid hazards
  - unlock passage
  - sequence actions
- Match current game state to strategy templates

Milestone 3.3 — Meta-Controller
- Decide when to:
  - explore
  - test action semantics
  - infer goal
  - plan
  - exploit known strategy
  - reset
- This becomes the “brain” of ASRA

Milestone 3.4 — Milestone #2 Submission
- Submit improved agent
- Compare against Milestone #1
- Document architectural improvements
```

```text
PHASE 4 — Robustness, Evaluation, and Optimization
Timeline: October 2026
Goal: Prepare final competitive submission

Milestone 4.1 — Failure Analysis
- Group failures by type:
  - poor exploration
  - wrong action inference
  - wrong goal inference
  - planner stuck
  - memory mismatch
  - too many wasted actions

Milestone 4.2 — Efficiency Optimization
- Reduce unnecessary actions
- Cache repeated states
- Prioritize informative actions
- Detect irreversible mistakes early
- Improve reset policy

Milestone 4.3 — Generalization Testing
- Test across many games and levels
- Hide game labels during testing
- Measure:
  - win rate
  - average actions to win
  - exploration cost
  - hypothesis accuracy
  - transfer across levels

Milestone 4.4 — Final Submission Candidate
- Freeze stable version
- Run repeated evaluations
- Keep backup versions
```

```text
PHASE 5 — Final Submission + Research Story
Timeline: November 2026
Goal: Submit agent + explain ASRA clearly

Milestone 5.1 — Final Kaggle Submission
- Submit before November 2, 2026
- Include clean repo
- Include reproducible instructions
- Include logs and evaluation notes

Milestone 5.2 — Paper / Writeup
- Submit paper-style explanation before November 8, 2026
- Explain:
  - why ASRA is not just an LLM wrapper
  - how it explores
  - how it infers action semantics
  - how it forms hypotheses
  - how it transfers strategies across levels

Milestone 5.3 — Demo Assets
- Create diagrams:
  - ASRA architecture
  - exploration graph
  - hypothesis loop
  - memory system
  - planner loop
- Create short video:
  - problem
  - ASRA idea
  - agent behavior
  - results
```

## What you should build first

Start with this order:

```text
1. ARC-AGI-3 environment runner
2. Frame differencing system
3. State-action-next-state graph
4. Exploration policy
5. Action semantics inference
6. Goal hypothesis engine
7. Planner
8. Cross-level memory
9. Submission pipeline
10. Paper/demo/writeup
```

## Your core project claim

**ASRA is an adaptive reasoning architecture that treats intelligence as scientific exploration: observe, act, compare, hypothesize, plan, and transfer strategies across unfamiliar environments.**

That aligns very well with ARC-AGI-3, because the benchmark specifically tests exploration, goal inference, internal world modeling, and adaptation in unseen interactive environments. ([ARC Prize][3])

[1]: https://arcprize.org/competitions/2026/arc-agi-3?utm_source=chatgpt.com "ARC Prize 2026 - ARC-AGI-3 Competition"
[2]: https://arxiv.org/abs/2512.24156?utm_source=chatgpt.com "Graph-Based Exploration for ARC-AGI-3 Interactive Reasoning Tasks"
[3]: https://arcprize.org/arc-agi/3?utm_source=chatgpt.com "ARC-AGI-3"
