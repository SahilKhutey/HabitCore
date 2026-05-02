"""
DriverMapper — energy accounting engine.

Tracks what drains and fuels a user's behavioral capacity.
This is the "environment shaping" layer of behavior change:
understanding the external inputs that affect consistency.

Social patterns (toxic vs. supportive) are also tracked here.

Output used by:
  InsightBuilder  — driver-based insights
  AICoachService  — "X is consistently draining your energy" context
  Progress evaluator — driver-adjusted score

v2 language: insights are specific and non-judgmental.
"""
from typing import List, Dict, Any, Optional
from collections import Counter


class DriverMapper:
    """Stateless energy driver analysis."""

    @staticmethod
    def map_drivers(logs: List[Any]) -> Dict[str, Any]:
        """
        Aggregate energy drivers across all logs.
        Returns ranked drainers, givers, and social pattern analysis.
        """
        all_drainers:  List[str] = []
        all_givers:    List[str] = []
        positive_social: List[str] = []
        negative_social: List[str] = []

        for log in logs:
            if isinstance(log.energy_drainers, list):
                all_drainers.extend(log.energy_drainers)
            if isinstance(log.energy_givers, list):
                all_givers.extend(log.energy_givers)
            if isinstance(log.social_influence, dict):
                positive_social.extend(log.social_influence.get("positive", []))
                negative_social.extend(log.social_influence.get("negative", []))

        top_drainers = DriverMapper._rank(all_drainers, top_n=5)
        top_givers   = DriverMapper._rank(all_givers,   top_n=5)
        social_patterns = DriverMapper._detect_social_patterns(
            positive_social, negative_social
        )

        return {
            "top_drainers":         top_drainers,
            "top_givers":           top_givers,
            "social_patterns":      social_patterns,
            "energy_balance":       DriverMapper._compute_balance(len(all_givers), len(all_drainers)),
            "dominant_drainer":     top_drainers[0]["item"] if top_drainers else None,
            "dominant_giver":       top_givers[0]["item"]   if top_givers else None,
        }

    @staticmethod
    def _rank(items: List[str], top_n: int = 5) -> List[Dict[str, Any]]:
        if not items:
            return []
        normalized = [i.lower().strip() for i in items if i.strip()]
        freq = Counter(normalized)
        total = len(normalized)
        return [
            {
                "item":      item,
                "frequency": count,
                "rate":      round(count / total, 3),
            }
            for item, count in freq.most_common(top_n)
        ]

    @staticmethod
    def _detect_social_patterns(
        positive: List[str],
        negative: List[str],
    ) -> Dict[str, Any]:
        """
        Detect whether social environment is net positive or net negative.
        Returns the most frequently cited toxic and supportive influences.
        """
        pos_freq = Counter([p.lower().strip() for p in positive])
        neg_freq = Counter([n.lower().strip() for n in negative])

        total = len(positive) + len(negative)
        if total == 0:
            return {"net": "neutral", "top_supportive": [], "top_toxic": []}

        net_score = (len(positive) - len(negative)) / total

        return {
            "net":            "positive" if net_score > 0.1 else ("negative" if net_score < -0.1 else "mixed"),
            "net_score":      round(net_score, 3),
            "top_supportive": [k for k, _ in pos_freq.most_common(3)],
            "top_toxic":      [k for k, _ in neg_freq.most_common(3)],
        }

    @staticmethod
    def _compute_balance(givers: int, drainers: int) -> str:
        """Overall energy accounting assessment."""
        if drainers == 0 and givers == 0:
            return "unknown"
        total = givers + drainers
        giver_ratio = givers / total
        if giver_ratio > 0.65:  return "surplus"
        if giver_ratio < 0.35:  return "deficit"
        return "balanced"

    @staticmethod
    def generate_driver_insights(driver_map: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Generate specific driver insights in v2 language.
        Called by InsightBuilder.
        """
        insights = []

        dominant_drainer = driver_map.get("dominant_drainer")
        if dominant_drainer:
            insights.append({
                "type":       "driver",
                "category":   "energy",
                "message":    f"'{dominant_drainer.title()}' appears as your most frequent energy drainer.",
                "action_hint": f"Identify one way to reduce exposure to or the impact of '{dominant_drainer}'.",
            })

        dominant_giver = driver_map.get("dominant_giver")
        if dominant_giver:
            insights.append({
                "type":       "driver",
                "category":   "energy",
                "message":    f"'{dominant_giver.title()}' consistently appears as an energy source.",
                "action_hint": f"Protect time for '{dominant_giver}' on low-energy days.",
            })

        social = driver_map.get("social_patterns", {})
        if social.get("net") == "negative" and social.get("top_toxic"):
            toxic = social["top_toxic"][0]
            insights.append({
                "type":       "driver",
                "category":   "social",
                "message":    f"Your social environment shows a net negative energy pattern. '{toxic.title()}' is cited most frequently.",
                "action_hint": "Consider adjusting frequency or quality of interactions that drain you.",
            })

        energy_balance = driver_map.get("energy_balance")
        if energy_balance == "deficit":
            insights.append({
                "type":       "driver",
                "category":   "energy",
                "message":    "Your energy inputs are consistently outweighed by drains. This pattern degrades behavioral consistency over time.",
                "action_hint": "Prioritize one energy-giving activity per day before optional commitments.",
            })

        return insights
