```text
You are an expert AI systems engineer and debugging assistant.

I have an ASRA Phase 1 transition dataset exported as JSONL.

Your task is to verify HASH STABILITY for state hashing.

Goal:
Ensure that:

same grid → always produces same state_hash

This is critical because ASRA uses state hashes for:
- memory
- state graphs
- cycle detection
- replay
- planning
- world modeling

==================================================
INPUT FILE
==================================================

Use this file:

/mnt/data/asra_v0_1_transitions.jsonl

==================================================
TASKS
==================================================

1. Load the JSONL transition dataset.

2. Inspect both:
- state
- next_state

inside every transition row.

3. For every grid:
- convert grid into a deterministic comparable representation
- group identical grids together

4. Verify:
same grid always maps to exactly one hash.

5. Detect instability cases where:
same grid → multiple hashes

6. Produce a detailed diagnostic report.

==================================================
IMPORTANT RULES
==================================================

The hash must ONLY depend on:
- grid values
- grid shape

The hash must NOT depend on:
- timestamp
- episode_id
- transition_id
- step_index
- metadata
- reward
- UUIDs
- random values

==================================================
OUTPUT REQUIREMENTS
==================================================

Generate:

1. Total transitions analyzed
2. Total unique grids
3. Total unique hashes
4. Number of unstable grids
5. Detailed instability examples if any exist

==================================================
EXPECTED OUTPUT FORMAT
==================================================

Example:

==================================================
HASH STABILITY REPORT
==================================================

Total transitions analyzed: 10234
Total grids analyzed: 20468
Unique grids: 1834
Unique hashes: 1834

RESULT:
✅ Hash stability PASSED

Every identical grid maps to exactly one hash.

==================================================

OR:

==================================================
HASH STABILITY REPORT
==================================================

RESULT:
❌ Hash instability DETECTED

Found 3 unstable grids.

Example #1
----------------------------------------
Grid:
[[0,0,1],
 [0,1,0]]

Hashes found:
- abc123
- xyz789

Possible cause:
metadata or timestamps included in hashing

==================================================

7. Also generate:
- top repeated grids
- their visit counts
- associated hashes

8. Compute:
- hash collision count
- whether different grids accidentally map to same hash

==================================================
ADDITIONAL ANALYSIS
==================================================

Also analyze:

1. Determinism:
Does:
same state + same action
→ same next_state ?

2. State reuse:
Which states appear most often?

3. Cycle likelihood:
Which state hashes repeatedly transition among themselves?

4. Action consistency:
Does ACTION1 consistently produce similar grid changes?

==================================================
VISUALIZATION REQUIREMENTS
==================================================

Generate:
1. Hash frequency histogram
2. State visit distribution
3. Most connected states
4. Transition graph statistics

If possible:
- build a NetworkX graph
- visualize state transition graph
- highlight repeated cycles

==================================================
TECHNICAL REQUIREMENTS
==================================================

Use:
- Python
- pandas
- collections.defaultdict
- hashlib
- networkx
- matplotlib

Write clean modular code.

Create functions:

- load_transitions()
- verify_hash_stability()
- detect_hash_collisions()
- analyze_determinism()
- analyze_state_reuse()
- build_transition_graph()
- visualize_statistics()

==================================================
SAVE OUTPUTS
==================================================

Save:
- hash_stability_report.txt
- unstable_grids.json
- state_statistics.csv
- transition_graph.graphml
- transition_graph.png

==================================================
SUCCESS CRITERIA
==================================================

The analysis is successful if we can confidently conclude:

1. identical grids always produce identical hashes
2. different grids do not collide
3. ASRA memory infrastructure is reliable
4. state graph construction is trustworthy
5. replay and cycle detection can be built safely on top of hashes

==================================================
FINAL GOAL
==================================================

This analysis validates whether ASRA's foundational memory identity system is correct.

Without stable hashes:
- memory breaks
- graphs break
- replay breaks
- planning breaks
- world models break

So this validation is mission-critical for ASRA Phase 1.
```
