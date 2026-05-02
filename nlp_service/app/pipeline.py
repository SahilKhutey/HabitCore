from app.utils.preprocess import clean_text
from app.extractors.emotion import detect_emotion
from app.extractors.behavior import extract_behaviors
from app.extractors.distortion import detect_distortions
from app.extractors.state import detect_state


def signals_to_events(signals):
    events = []

    for b in signals["behaviors"]:
        events.append({
            "event_type": b,
            "event_value": 1
        })

    if signals["state"] == "avoidance":
        events.append({"event_type": "task_avoided"})

    return events


def process_text(user_id: str, text: str):
    cleaned = clean_text(text)

    signals = {
        "user_id": user_id,
        "emotion": detect_emotion(cleaned),
        "state": detect_state(cleaned),
        "behaviors": extract_behaviors(cleaned),
        "distortions": detect_distortions(cleaned),
    }

    signals["events"] = signals_to_events(signals)

    return signals
