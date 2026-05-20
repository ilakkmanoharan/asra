### Slide 1: Cinematic Intro

A-S-R-A Phase 1 is about adaptive experimental memory formation. Before an agent can reason scientifically, it must learn to observe unknown worlds, act without assumed semantics, and remember what happened.

### Slide 2: Static vs Interactive

Traditional AI often excels at static benchmarks. But real intelligence unfolds inside environments that change when we act. A-S-R-A treats intelligence as adaptive experimentation in unknown environments.

### Slide 3: Introducing A-S-R-A

A-S-R-A, the Adaptive Scientific Reasoning Architecture, is built for interactive scientific learning. Phase one does not memorize tasks. It builds the infrastructure to observe, experiment, and remember.

### Slide 4: What Is Phase 1

Phase one is adaptive experimental memory formation. The agent watches frames, tests actions, compares states, logs transitions, builds a state graph, replays episodes, and exports datasets.

### Slide 5: ARC-AGI-3

ARC AGI three provides interactive grid worlds. Each frame is parsed into a normalized grid. Actions are available, but their semantics are not given. The agent must discover effects through experimentation.

### Slide 6: Architecture

The Phase one pipeline connects an environment runner, frame parser, exploration policy, action execution, grid differencing, state hashing, episode logger, state graph, replay viewer, and dataset exporter into one reproducible system.

### Slide 7: Transitions

Every step becomes a transition: state, action, next state, reward, terminal flag, and metadata. This is the atomic unit of experiential memory.

### Slide 8: Grid Diff

Grid differencing highlights which cells changed, how much of the grid changed, and which colors appeared or disappeared. This is how A-S-R-A sees action consequences.

### Slide 9: State Hash

Identical grids always receive the same SHA-256 state hash. That stable identity powers the state graph, replay, and cycle detection.

### Slide 10: State Graph

Transitions accumulate into a state graph. Nodes are unique states. Edges are actions with counts, rewards, and diff summaries. Exploration topology becomes visible.

### Slide 11: Exploration Policy

The baseline simple exploration policy prefers untested actions and new state hashes, avoids game over and cycles, and resets when dead-end scores grow high.

### Slide 12: Dead Ends

Dead-end detection flags states where every action fails to escape, where grids stop changing, or where the agent loops among known states.

### Slide 13: Replay

The replay viewer walks step by step through episodes, showing grids before and after, diffs, rewards, and metadata. Memory becomes inspectable science.

### Slide 14: Exports

Phase one exports transitions as JSONL and Parquet, episode summaries as CSV, and the state graph as JSON for analysis, visualization, and future learning.

### Slide 15: Accomplished

A-S-R-A can now interact, observe, compare, remember, replay, graph, and export. This is not hypothetical. Phase one built the memory layer.

### Slide 16: Future Phases

Phase two will infer action semantics. Phase three builds world models. Phase four invents strategies. Phase five pursues scientific reasoning. But all of it stands on Phase one's memory.

### Slide 17: Closing

Before intelligence can reason, it must first learn to observe, experiment, and remember. A-S-R-A Phase one is that foundation. This is the beginning of adaptive experimental intelligence.