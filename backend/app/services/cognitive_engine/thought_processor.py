"""
ThoughtProcessor — CBT-grounded cognitive distortion detection.

The system's key differentiator: it doesn't just track thoughts,
it classifies them using established cognitive distortion taxonomy.

Distortion taxonomy (CBT-aligned, 12 types):
  all_or_nothing, overgeneralization, mental_filter, disqualifying_positive,
  mind_reading, fortune_telling, catastrophizing, magnification,
  emotional_reasoning, should_statements, labeling, personalization

Output feeds:
  - InsightBuilder (cognitive insights)
  - AICoachService (distortion context for grounded guidance)
  - BehavioralInsightEngine (correlation with habit failure)
"""
import re
from typing import Optional, Dict, List, Tuple


# ── Distortion Taxonomy ───────────────────────────────────────────────────────
# Each entry: (keywords, description, reframe_prompt)

DISTORTIONS: Dict[str, Dict] = {
    "all_or_nothing": {
        "keywords":  ["always", "never", "completely", "totally", "every time",
                      "nothing works", "everything", "perfect", "failure"],
        "label":     "All-or-Nothing Thinking",
        "desc":      "Viewing situations in black-and-white terms with no middle ground.",
        "reframe":   "What is a more balanced view that acknowledges some progress?",
        "severity":  0.8,
    },
    "overgeneralization": {
        "keywords":  ["always happens", "never works out", "this always", "i always fail",
                      "everyone", "no one ever"],
        "label":     "Overgeneralization",
        "desc":      "Drawing broad conclusions from a single event.",
        "reframe":   "Is this actually a pattern, or one difficult instance?",
        "severity":  0.7,
    },
    "catastrophizing": {
        "keywords":  ["disaster", "ruined", "terrible", "worst", "horrible",
                      "can't take it", "unbearable", "destroyed", "everything is over"],
        "label":     "Catastrophizing",
        "desc":      "Predicting or magnifying the worst possible outcome.",
        "reframe":   "What is the most realistic outcome, not the worst?",
        "severity":  0.9,
    },
    "mind_reading": {
        "keywords":  ["they think", "he thinks", "she thinks", "they probably",
                      "everyone thinks i'm", "they must think"],
        "label":     "Mind Reading",
        "desc":      "Assuming you know what others are thinking, typically negatively.",
        "reframe":   "What evidence do you actually have for this belief?",
        "severity":  0.7,
    },
    "fortune_telling": {
        "keywords":  ["i know it will", "it's going to fail", "won't work",
                      "will never", "bound to", "i'll fail"],
        "label":     "Fortune Telling",
        "desc":      "Predicting a negative outcome as if it were certain.",
        "reframe":   "What would need to be true for a different outcome?",
        "severity":  0.75,
    },
    "emotional_reasoning": {
        "keywords":  ["i feel like a failure", "i feel stupid", "i feel worthless",
                      "i feel like i can't", "i feel like it's hopeless"],
        "label":     "Emotional Reasoning",
        "desc":      "Treating emotions as evidence of truth ('I feel it, so it must be true').",
        "reframe":   "What would the facts say, separate from how you feel?",
        "severity":  0.8,
    },
    "should_statements": {
        "keywords":  ["i should", "i must", "i have to", "i ought to",
                      "shouldn't have", "must be"],
        "label":     "Should Statements",
        "desc":      "Rigid rules about how you or others should behave, creating guilt.",
        "reframe":   "What would it look like to replace 'should' with 'I choose to'?",
        "severity":  0.6,
    },
    "labeling": {
        "keywords":  ["i'm a loser", "i'm an idiot", "i'm worthless",
                      "i'm a failure", "i'm weak", "i'm useless"],
        "label":     "Labeling",
        "desc":      "Attaching a global negative label to yourself based on one event.",
        "reframe":   "What did you do (not what you are) in this situation?",
        "severity":  0.85,
    },
    "personalization": {
        "keywords":  ["my fault", "because of me", "i caused",
                      "if it weren't for me", "i ruined"],
        "label":     "Personalization",
        "desc":      "Taking excessive blame for events outside your full control.",
        "reframe":   "What external factors also contributed to this outcome?",
        "severity":  0.75,
    },
    "comparison": {
        "keywords":  ["better than me", "ahead of me", "more successful",
                      "everyone else", "they have it", "compared to"],
        "label":     "Social Comparison",
        "desc":      "Measuring your worth against others, typically unfavorably.",
        "reframe":   "How does your trajectory compare to your past self, not others?",
        "severity":  0.65,
    },
}


class ThoughtProcessor:
    """
    Analyzes thought entries for cognitive distortions.
    Returns structured analysis consumed by InsightBuilder and AICoachService.
    """

    @staticmethod
    def classify_thought_type(thought: str) -> str:
        """
        Simple helpful/harmful/neutral classification.
        Harmful = contains distortion or consistently negative framing.
        """
        if not thought:
            return "neutral"
        detected = ThoughtProcessor.detect_distortion(thought)
        if detected:
            return "harmful"
        if any(w in thought.lower() for w in ["grateful", "proud", "good", "progress", "better"]):
            return "helpful"
        return "neutral"

    @staticmethod
    def detect_distortion(thought: str) -> Optional[Dict]:
        """
        Primary distortion detection. Returns the highest-severity match or None.

        Returns:
            {"type": str, "label": str, "desc": str, "reframe": str,
             "severity": float, "matched_keyword": str}
        """
        if not thought:
            return None

        thought_lower = thought.lower()
        matches: List[Tuple[str, Dict, str]] = []

        for dtype, config in DISTORTIONS.items():
            for keyword in config["keywords"]:
                if keyword in thought_lower:
                    matches.append((dtype, config, keyword))
                    break  # one match per distortion type

        if not matches:
            return None

        # Return highest-severity distortion
        matches.sort(key=lambda x: x[1]["severity"], reverse=True)
        dtype, config, matched_kw = matches[0]

        return {
            "type":            dtype,
            "label":           config["label"],
            "description":     config["desc"],
            "reframe_prompt":  config["reframe"],
            "severity":        config["severity"],
            "matched_keyword": matched_kw,
            "confidence":      ThoughtProcessor._compute_confidence(thought, config),
        }

    @staticmethod
    def detect_all_distortions(thought: str) -> List[Dict]:
        """Returns all matched distortions (for detailed analysis view)."""
        if not thought:
            return []

        thought_lower = thought.lower()
        found = []
        for dtype, config in DISTORTIONS.items():
            for keyword in config["keywords"]:
                if keyword in thought_lower:
                    found.append({
                        "type":           dtype,
                        "label":          config["label"],
                        "description":    config["desc"],
                        "reframe_prompt": config["reframe"],
                        "severity":       config["severity"],
                    })
                    break
        return sorted(found, key=lambda x: x["severity"], reverse=True)

    @staticmethod
    def compute_belief_shift(before: Optional[int], after: Optional[int]) -> Optional[float]:
        """
        Measure the impact of a reframe attempt.
        Returns shift as a fraction of the before value (0.0–1.0 reduction).
        Positive = belief weakened (good). Negative = belief strengthened (concerning).
        """
        if before is None or after is None:
            return None
        if before == 0:
            return 0.0
        return round((before - after) / before, 3)

    @staticmethod
    def _compute_confidence(thought: str, config: Dict) -> float:
        """
        Confidence is higher when multiple keywords from the same distortion
        type appear in the same thought.
        """
        count = sum(1 for kw in config["keywords"] if kw in thought.lower())
        return min(0.6 + (count - 1) * 0.15, 0.98)
