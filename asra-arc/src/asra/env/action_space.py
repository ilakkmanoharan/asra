SUPPORTED_ACTIONS = ["RESET", "ACTION1", "ACTION2", "ACTION3", "ACTION4", "ACTION5", "ACTION6", "ACTION7"]


def action_index(action: str) -> int:
    if action not in SUPPORTED_ACTIONS:
        raise ValueError(f"Unsupported action: {action}")
    return SUPPORTED_ACTIONS.index(action)
