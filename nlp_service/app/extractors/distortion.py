DISTORTIONS = {
    "always": "overgeneralization",
    "never": "all_or_nothing",
    "everyone": "mind_reading",
    "nothing works": "hopelessness"
}

def detect_distortions(text: str):
    return [v for k, v in DISTORTIONS.items() if k in text]
