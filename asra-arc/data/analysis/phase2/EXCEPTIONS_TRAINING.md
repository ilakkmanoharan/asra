# Phase 2 exception tasks — training

Tasks where top rule `confidence < 1.0` (inconsistent cross-demo pattern): **8**

## `22eb0ac0`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_CREATE` (confidence=0.6666666666666666, support=2)
- **Demo transform summaries:** 12 events: CREATE, DELETE, ROTATE, 8 events: IDENTITY, 9 events: CREATE, DELETE, IDENTITY, ROTATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 8 | 7 | 9 | 9 events: CREATE, DELETE, IDENTITY, ROTATE |
| train_1 | 10 | 8 | 12 | 12 events: CREATE, DELETE, ROTATE |
| train_2 | 8 | 8 | 8 | 8 events: IDENTITY |

**Rule candidates:**
- `PER_OBJECT_CREATE` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_DELETE` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_IDENTITY` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_ROTATE` — confidence=0.6666666666666666, support=2

## `67385a82`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_IDENTITY` (confidence=0.75, support=3)
- **Demo transform summaries:** 2 events: CREATE, IDENTITY, 4 events: CREATE, DELETE, ROTATE, 4 events: IDENTITY, ROTATE, 5 events: IDENTITY, ROTATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 3 | 3 | 4 | 4 events: CREATE, DELETE, ROTATE |
| train_1 | 4 | 4 | 4 | 4 events: IDENTITY, ROTATE |
| train_2 | 1 | 2 | 2 | 2 events: CREATE, IDENTITY |
| train_3 | 5 | 5 | 5 | 5 events: IDENTITY, ROTATE |

**Rule candidates:**
- `PER_OBJECT_IDENTITY` — confidence=0.75, support=3
- `PER_OBJECT_ROTATE` — confidence=0.75, support=3
- `PER_OBJECT_CREATE` — confidence=0.5, support=2
- `PER_OBJECT_DELETE` — confidence=0.25, support=1

## `794b24be`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_CREATE` (confidence=0.8, support=8)
- **Demo transform summaries:** 2 events: CREATE, DELETE, 3 events: CREATE, DELETE, 4 events: CREATE, DELETE, ROTATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 1 | 1 | 1 | ROTATE |
| train_1 | 2 | 1 | 3 | 3 events: CREATE, DELETE |
| train_2 | 2 | 1 | 3 | 3 events: CREATE, DELETE |
| train_3 | 2 | 1 | 3 | 3 events: CREATE, DELETE |
| train_4 | 1 | 1 | 1 | ROTATE |
| train_5 | 2 | 1 | 3 | 3 events: CREATE, DELETE |
| train_6 | 1 | 1 | 2 | 2 events: CREATE, DELETE |
| train_7 | 3 | 1 | 4 | 4 events: CREATE, DELETE |
| train_8 | 1 | 1 | 2 | 2 events: CREATE, DELETE |
| train_9 | 2 | 1 | 3 | 3 events: CREATE, DELETE |

**Rule candidates:**
- `PER_OBJECT_CREATE` — confidence=0.8, support=8
- `PER_OBJECT_DELETE` — confidence=0.8, support=8
- `PER_OBJECT_ROTATE` — confidence=0.2, support=2

## `9565186b`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_CREATE` (confidence=0.75, support=3)
- **Demo transform summaries:** 3 events: CREATE, DELETE, 4 events: CREATE, DELETE, 5 events: CREATE, DELETE, ROTATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 2 | 1 | 3 | 3 events: CREATE, DELETE |
| train_1 | 3 | 1 | 4 | 4 events: CREATE, DELETE |
| train_2 | 1 | 1 | 1 | ROTATE |
| train_3 | 4 | 1 | 5 | 5 events: CREATE, DELETE |

**Rule candidates:**
- `PER_OBJECT_CREATE` — confidence=0.75, support=3
- `PER_OBJECT_DELETE` — confidence=0.75, support=3
- `PER_OBJECT_ROTATE` — confidence=0.25, support=1

## `a740d043`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_DELETE` (confidence=0.6666666666666666, support=2)
- **Demo transform summaries:** 2 events: DELETE, TRANSLATE, 2 events: ROTATE, TRANSLATE, 4 events: CREATE, DELETE, ROTATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 3 | 3 | 4 | 4 events: CREATE, DELETE, ROTATE |
| train_1 | 2 | 2 | 2 | 2 events: ROTATE, TRANSLATE |
| train_2 | 2 | 1 | 2 | 2 events: DELETE, TRANSLATE |

**Rule candidates:**
- `PER_OBJECT_DELETE` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_ROTATE` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_TRANSLATE` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_CREATE` — confidence=0.3333333333333333, support=1

## `aedd82e4`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_ROTATE` (confidence=0.75, support=3)
- **Demo transform summaries:** 3 events: IDENTITY, ROTATE, 4 events: CREATE, DELETE, 5 events: CREATE, DELETE, ROTATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 2 | 2 | 4 | 4 events: CREATE, DELETE |
| train_1 | 3 | 3 | 3 | 3 events: IDENTITY, ROTATE |
| train_2 | 3 | 3 | 3 | 3 events: IDENTITY, ROTATE |
| train_3 | 4 | 3 | 5 | 5 events: CREATE, DELETE, ROTATE |

**Rule candidates:**
- `PER_OBJECT_ROTATE` — confidence=0.75, support=3
- `PER_OBJECT_CREATE` — confidence=0.5, support=2
- `PER_OBJECT_DELETE` — confidence=0.5, support=2
- `PER_OBJECT_IDENTITY` — confidence=0.5, support=2

## `b1948b0a`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_ROTATE` (confidence=0.6666666666666666, support=2)
- **Demo transform summaries:** 2 events: IDENTITY, 4 events: ROTATE, 5 events: ROTATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 2 | 2 | 2 | 2 events: IDENTITY |
| train_1 | 5 | 5 | 5 | 5 events: ROTATE |
| train_2 | 4 | 4 | 4 | 4 events: ROTATE |

**Rule candidates:**
- `PER_OBJECT_ROTATE` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_IDENTITY` — confidence=0.3333333333333333, support=1

## `cce03e0d`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_CREATE` (confidence=0.6666666666666666, support=2)
- **Demo transform summaries:** 28 events: CREATE, ROTATE, 4 events: TRANSLATE, 6 events: CREATE, TRANSLATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 4 | 4 | 4 | 4 events: TRANSLATE |
| train_1 | 3 | 6 | 6 | 6 events: CREATE, TRANSLATE |
| train_2 | 5 | 28 | 28 | 28 events: CREATE, ROTATE |

**Rule candidates:**
- `PER_OBJECT_CREATE` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_TRANSLATE` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_ROTATE` — confidence=0.3333333333333333, support=1
