from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

_ENV_PATTERN = re.compile(r"\$\{([^}]+)\}")


def load_config(path: str | Path) -> dict[str, Any]:
    text = Path(path).read_text(encoding="utf-8")
    text = _ENV_PATTERN.sub(lambda match: os.getenv(match.group(1), ""), text)
    return yaml.safe_load(text) or {}
