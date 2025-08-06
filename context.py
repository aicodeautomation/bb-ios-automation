from config import CONFIGS

# Global variable to hold the current context
CURRENT_CONTEXT = {
    "target": None,
    "config": None
}

def set_context(target_id: int):
    """Sets global context based on target_id."""
    if target_id not in CONFIGS:
        raise ValueError(f"No config found for target {target_id}")
    CURRENT_CONTEXT["target"] = target_id
    CURRENT_CONTEXT["config"] = CONFIGS[target_id]

def get_context():
    """Returns current config."""
    if CURRENT_CONTEXT["config"] is None:
        raise RuntimeError("Context has not been set.")
    return CURRENT_CONTEXT["config"]
