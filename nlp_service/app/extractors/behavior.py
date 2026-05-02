BEHAVIOR_MAP = {
    "scroll": "distraction",
    "youtube": "distraction",
    "avoid": "avoidance",
    "work": "deep_work",
    "study": "deep_work"
}

def extract_behaviors(text: str):
    return [v for k, v in BEHAVIOR_MAP.items() if k in text]
