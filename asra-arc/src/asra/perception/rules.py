from __future__ import annotations

from collections import Counter

from asra.perception.schemas import RuleCandidate, TransformClass, TransformDetection


def _demo_transform_types(det: TransformDetection) -> set[str]:
    types = {e.transform_class.value for e in det.events if e.transform_class != TransformClass.UNKNOWN}
    if not types:
        types = {TransformClass.IDENTITY.value}
    return types


def _dominant_transform_types(det: TransformDetection) -> list[str]:
    counts: Counter[str] = Counter(
        e.transform_class.value for e in det.events if e.transform_class != TransformClass.UNKNOWN
    )
    if not counts:
        return [TransformClass.IDENTITY.value]
    peak = counts.most_common(1)[0][1]
    return sorted(t for t, c in counts.items() if c == peak)


class RuleCandidateGenerator:
    """Heuristic rule templates from demo-pair transform detections."""

    def generate(self, demo_detections: list[TransformDetection]) -> list[RuleCandidate]:
        if not demo_detections:
            return []
        per_demo_types: list[set[str]] = [_demo_transform_types(det) for det in demo_detections]

        common = set.intersection(*per_demo_types) if per_demo_types else set()
        counts: Counter[str] = Counter()
        for det in demo_detections:
            for e in det.events:
                counts[e.transform_class.value] += 1

        candidates: list[RuleCandidate] = []
        support_all = len(demo_detections)
        needs_per_demo = len({frozenset(t) for t in per_demo_types}) > 1

        if common and not needs_per_demo:
            pattern = "APPLY_" + "_AND_".join(sorted(common)) + "_TO_MATCHED_OBJECTS"
            candidates.append(
                RuleCandidate(
                    rule_id="rule_common_transform",
                    pattern=pattern,
                    support=support_all,
                    confidence=1.0,
                    transform_types=sorted(common),
                    rule_scope="global",
                )
            )

        for tclass, _count in counts.most_common():
            support = sum(1 for types in per_demo_types if tclass in types)
            candidates.append(
                RuleCandidate(
                    rule_id=f"rule_{tclass.lower()}",
                    pattern=f"PER_OBJECT_{tclass}",
                    support=support,
                    confidence=support / support_all,
                    transform_types=[tclass],
                    rule_scope="global",
                )
            )

        if needs_per_demo:
            candidates.append(
                RuleCandidate(
                    rule_id="rule_branched_per_demo",
                    pattern="BRANCHED_PER_DEMO",
                    support=support_all,
                    confidence=1.0,
                    transform_types=[],
                    rule_scope="branched",
                )
            )
            for idx, det in enumerate(demo_detections):
                dominant = _dominant_transform_types(det)
                pattern = f"PER_DEMO_{idx}_" + "_AND_".join(dominant)
                candidates.append(
                    RuleCandidate(
                        rule_id=f"rule_per_demo_{idx}",
                        pattern=pattern,
                        support=1,
                        confidence=1.0,
                        transform_types=dominant,
                        rule_scope="per_demo",
                        demo_index=idx,
                    )
                )

        if not candidates:
            candidates.append(
                RuleCandidate(
                    rule_id="rule_identity",
                    pattern="NO_OBJECT_CHANGE",
                    support=support_all,
                    confidence=0.5,
                    transform_types=[TransformClass.IDENTITY.value],
                    rule_scope="global",
                )
            )

        def _sort_key(c: RuleCandidate) -> tuple:
            scope_rank = 0 if c.rule_scope == "branched" else (1 if c.rule_scope == "global" and c.confidence >= 1.0 else 2)
            return (scope_rank, -c.confidence, -c.support, c.rule_id)

        candidates.sort(key=_sort_key)
        return candidates
