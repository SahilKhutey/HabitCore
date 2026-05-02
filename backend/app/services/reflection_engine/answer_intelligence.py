"""
Answer Intelligence Engine — Extracts structured behavioral signals from user reflection text.
"""
import re
from typing import List, Dict, Any

EMOTION_MAP = {
    "sad": "sadness",
    "tired": "low_energy",
    "exhausted": "low_energy",
    "anxious": "anxiety",
    "stressed": "stress",
    "overwhelmed": "overwhelm",
    "happy": "positive",
    "proud": "positive",
    "angry": "anger",
    "frustrated": "frustration"
}

DISTORTIONS = {
    "always": "overgeneralization",
    "never": "all_or_nothing",
    "everyone": "mind_reading",
    "nothing works": "hopelessness",
    "should": "should_statement",
    "must": "should_statement",
    "worst": "catastrophizing"
}

BEHAVIOR_MAP = {
    "scroll": "distraction",
    "watched": "distraction",
    "avoided": "avoidance",
    "delayed": "avoidance",
    "pushed": "avoidance",
    "worked": "deep_work",
    "focused": "deep_work",
    "exercise": "self_care",
    "meditate": "self_care"
}

STATE_MAP = {
    "avoid": "avoidance",
    "overthinking": "rumination",
    "loop": "rumination",
    "flow": "flow",
    "focused": "flow",
    "clear": "clarity"
}

class AnswerIntelligence:
    @staticmethod
    def clean_text(text: str) -> str:
        if not text: return ""
        text = text.lower()
        text = re.sub(r"[^\w\s]", "", text)
        return text

    @classmethod
    def build_signals(cls, text: str) -> Dict[str, Any]:
        cleaned = cls.clean_text(text)
        
        # 1. Emotion Detection
        emotion = "neutral"
        for word, label in EMOTION_MAP.items():
            if word in cleaned:
                emotion = label
                break
                
        # 2. Thought Pattern Detection (Distortions)
        distortions = []
        for word, label in DISTORTIONS.items():
            if word in cleaned:
                distortions.append(label)
        
        # 3. Behavior Extraction
        behaviors = []
        for word, label in BEHAVIOR_MAP.items():
            if word in cleaned:
                behaviors.append(label)
                
        # 4. State Detection
        state = "neutral"
        for word, label in STATE_MAP.items():
            if word in cleaned:
                state = label
                break
                
        return {
            "emotion": emotion,
            "distortions": list(set(distortions)),
            "behaviors": list(set(behaviors)),
            "state": state,
            "raw_text": text
        }

    @staticmethod
    def map_to_events(signals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Maps signals back to the core Event system."""
        events = []
        
        for behavior in signals["behaviors"]:
            events.append({
                "event_type": f"extracted_{behavior}",
                "event_value": 1.0
            })
            
        if signals["state"] != "neutral":
            events.append({
                "event_type": f"state_{signals['state']}",
                "event_value": 1.0
            })
            
        return events
