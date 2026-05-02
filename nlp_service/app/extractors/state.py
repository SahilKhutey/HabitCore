def detect_state(text: str):
    if "avoid" in text:
        return "avoidance"
    if "overthink" in text:
        return "rumination"
    if "focus" in text:
        return "flow"
    return "neutral"
