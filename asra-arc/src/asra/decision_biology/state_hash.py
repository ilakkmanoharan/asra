from __future__ import annotations

import hashlib
import json
from typing import Any


def hash_biology_state(gene_activities: dict[str, float], pathway_id: str = "omnipath") -> str:
    payload = {"pathway_id": pathway_id, "gene_activities": dict(sorted(gene_activities.items()))}
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
