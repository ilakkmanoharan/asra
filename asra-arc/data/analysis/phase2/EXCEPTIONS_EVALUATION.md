# Phase 2 exception tasks — evaluation

Tasks where top rule `confidence < 1.0` (inconsistent cross-demo pattern): **9**

## `1990f7a8`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_TRANSLATE` (confidence=0.6666666666666666, support=2)
- **Demo transform summaries:** 11 events: TRANSLATE, 8 events: TRANSLATE, 9 events: CREATE, DELETE, ROTATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 8 | 4 | 9 | 9 events: CREATE, DELETE, ROTATE |
| train_1 | 8 | 8 | 8 | 8 events: TRANSLATE |
| train_2 | 11 | 11 | 11 | 11 events: TRANSLATE |

**Rule candidates:**
- `PER_OBJECT_TRANSLATE` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_CREATE` — confidence=0.3333333333333333, support=1
- `PER_OBJECT_DELETE` — confidence=0.3333333333333333, support=1
- `PER_OBJECT_ROTATE` — confidence=0.3333333333333333, support=1

## `32e9702f`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_CREATE` (confidence=0.6666666666666666, support=2)
- **Demo transform summaries:** 2 events: CREATE, DELETE, 2 events: TRANSLATE, 4 events: CREATE, DELETE, TRANSLATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 1 | 1 | 2 | 2 events: CREATE, DELETE |
| train_1 | 2 | 2 | 2 | 2 events: TRANSLATE |
| train_2 | 3 | 3 | 4 | 4 events: CREATE, DELETE, TRANSLATE |

**Rule candidates:**
- `PER_OBJECT_CREATE` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_DELETE` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_TRANSLATE` — confidence=0.6666666666666666, support=2

## `3391f8c0`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_ROTATE` (confidence=0.75, support=3)
- **Demo transform summaries:** 10 events: ROTATE, 5 events: ROTATE, 6 events: ROTATE, 8 events: CREATE, DELETE, TRANSLATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 6 | 6 | 6 | 6 events: ROTATE |
| train_1 | 5 | 5 | 5 | 5 events: ROTATE |
| train_2 | 7 | 5 | 8 | 8 events: CREATE, DELETE, TRANSLATE |
| train_3 | 10 | 10 | 10 | 10 events: ROTATE |

**Rule candidates:**
- `PER_OBJECT_ROTATE` — confidence=0.75, support=3
- `PER_OBJECT_CREATE` — confidence=0.25, support=1
- `PER_OBJECT_DELETE` — confidence=0.25, support=1
- `PER_OBJECT_TRANSLATE` — confidence=0.25, support=1

## `68b67ca3`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_IDENTITY` (confidence=0.6666666666666666, support=2)
- **Demo transform summaries:** 4 events: IDENTITY, TRANSLATE, 5 events: IDENTITY, TRANSLATE, 7 events: CREATE, DELETE, ROTATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 6 | 4 | 7 | 7 events: CREATE, DELETE, ROTATE |
| train_1 | 5 | 5 | 5 | 5 events: IDENTITY, TRANSLATE |
| train_2 | 4 | 4 | 4 | 4 events: IDENTITY, TRANSLATE |

**Rule candidates:**
- `PER_OBJECT_IDENTITY` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_TRANSLATE` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_CREATE` — confidence=0.3333333333333333, support=1
- `PER_OBJECT_DELETE` — confidence=0.3333333333333333, support=1
- `PER_OBJECT_ROTATE` — confidence=0.3333333333333333, support=1

## `8a371977`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_ROTATE` (confidence=0.6666666666666666, support=2)
- **Demo transform summaries:** 121 events: ROTATE, 37 events: CREATE, DELETE, 9 events: ROTATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 9 | 9 | 9 | 9 events: ROTATE |
| train_1 | 121 | 121 | 121 | 121 events: ROTATE |
| train_2 | 1 | 36 | 37 | 37 events: CREATE, DELETE |

**Rule candidates:**
- `PER_OBJECT_ROTATE` — confidence=0.6666666666666666, support=2
- `PER_OBJECT_CREATE` — confidence=0.3333333333333333, support=1
- `PER_OBJECT_DELETE` — confidence=0.3333333333333333, support=1

## `d017b73f`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_TRANSLATE` (confidence=0.75, support=3)
- **Demo transform summaries:** 3 events: IDENTITY, TRANSLATE, 3 events: ROTATE, TRANSLATE, 4 events: CREATE, DELETE, IDENTITY, 4 events: ROTATE, TRANSLATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 3 | 3 | 3 | 3 events: IDENTITY, TRANSLATE |
| train_1 | 4 | 4 | 4 | 4 events: ROTATE, TRANSLATE |
| train_2 | 3 | 3 | 3 | 3 events: ROTATE, TRANSLATE |
| train_3 | 3 | 2 | 4 | 4 events: CREATE, DELETE, IDENTITY |

**Rule candidates:**
- `PER_OBJECT_TRANSLATE` — confidence=0.75, support=3
- `PER_OBJECT_IDENTITY` — confidence=0.5, support=2
- `PER_OBJECT_ROTATE` — confidence=0.5, support=2
- `PER_OBJECT_CREATE` — confidence=0.25, support=1
- `PER_OBJECT_DELETE` — confidence=0.25, support=1

## `d4b1c2b1`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_CREATE` (confidence=0.7142857142857143, support=5)
- **Demo transform summaries:** 12 events: CREATE, DELETE, 2 events: CREATE, DELETE, 4 events: CREATE, DELETE, 6 events: CREATE, DELETE, IDENTITY

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 2 | 2 | 4 | 4 events: CREATE, DELETE |
| train_1 | 2 | 2 | 4 | 4 events: CREATE, DELETE |
| train_2 | 6 | 6 | 12 | 12 events: CREATE, DELETE |
| train_3 | 0 | 0 | 0 | IDENTITY |
| train_4 | 0 | 0 | 0 | IDENTITY |
| train_5 | 1 | 1 | 2 | 2 events: CREATE, DELETE |
| train_6 | 3 | 3 | 6 | 6 events: CREATE, DELETE |

**Rule candidates:**
- `PER_OBJECT_CREATE` — confidence=0.7142857142857143, support=5
- `PER_OBJECT_DELETE` — confidence=0.7142857142857143, support=5

## `e78887d1`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_DELETE` (confidence=0.75, support=3)
- **Demo transform summaries:** 12 events: DELETE, TRANSLATE, 14 events: DELETE, ROTATE, 16 events: DELETE, ROTATE, 7 events: ROTATE, TRANSLATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 12 | 4 | 12 | 12 events: DELETE, TRANSLATE |
| train_1 | 14 | 7 | 14 | 14 events: DELETE, ROTATE |
| train_2 | 7 | 7 | 7 | 7 events: ROTATE, TRANSLATE |
| train_3 | 16 | 8 | 16 | 16 events: DELETE, ROTATE |

**Rule candidates:**
- `PER_OBJECT_DELETE` — confidence=0.75, support=3
- `PER_OBJECT_ROTATE` — confidence=0.75, support=3
- `PER_OBJECT_TRANSLATE` — confidence=0.5, support=2

## `fc754716`

- **Likely cause:** mixed_transform_types_across_demos
- **Top rule:** `PER_OBJECT_CREATE` (confidence=0.75, support=3)
- **Demo transform summaries:** 2 events: CREATE, DELETE, ROTATE

| pair | input objs | output objs | events | summary |
|------|------------|-------------|--------|---------|
| train_0 | 1 | 1 | 1 | ROTATE |
| train_1 | 1 | 1 | 2 | 2 events: CREATE, DELETE |
| train_2 | 1 | 1 | 2 | 2 events: CREATE, DELETE |
| train_3 | 1 | 1 | 2 | 2 events: CREATE, DELETE |

**Rule candidates:**
- `PER_OBJECT_CREATE` — confidence=0.75, support=3
- `PER_OBJECT_DELETE` — confidence=0.75, support=3
- `PER_OBJECT_ROTATE` — confidence=0.25, support=1
