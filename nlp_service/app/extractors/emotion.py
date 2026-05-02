EMOTION_MAP = {
    "sad": "sadness",
    "tired": "low_energy",
    "anxious": "anxiety",
    "stress": "stress",
    "happy": "positive",
    "angry": "anger"
}

def detect_emotion(text: str) -> str:
    for k, v in EMOTION_MAP.items():
        if k in text:
            return v
    return "neutral"
