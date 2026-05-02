"""
Insight Generator — Converts patterns and stats into actionable user feedback.
"""
from typing import List, Dict, Any

def generate_insights(patterns: List[Dict[str, Any]], stats: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Synthesizes detected patterns and statistical correlations into a prioritized list of insights.
    """
    insights = []

    # Map patterns to insights
    for p in patterns:
        if p["type"] == "energy_avoidance":
            insights.append({
                "type": "pattern",
                "title": "Energy Management",
                "message": "Your data shows a strong link between low energy and task avoidance. Protect your sleep and recovery to maintain momentum.",
                "priority": 0.9
            })
        elif p["type"] == "distraction_mood_impact":
            insights.append({
                "type": "warning",
                "title": "Focus-Mood Connection",
                "message": "High distraction days seem to impact your emotional state the following day. Consider a focus-first morning tomorrow.",
                "priority": 0.8
            })
        elif p["type"] == "unframed_negativity_loop":
            insights.append({
                "type": "intervention",
                "title": "Cognitive Loop Detected",
                "message": "Negative thoughts are persisting without reframing. Try a 5-minute 'worst-case' audit to break the loop.",
                "priority": 0.95
            })

    # Map significant correlations to insights
    if stats.get("distraction_mood_corr", 0) < -0.6:
        insights.append({
            "type": "statistical",
            "title": "Deep Insight",
            "message": "There is a strong negative correlation between your distraction levels and your mood. Reducing noise is your fastest path to feeling better.",
            "priority": 0.75
        })

    # Sort by priority and limit to top 2 to avoid overwhelm
    insights.sort(key=lambda x: x["priority"], reverse=True)
    
    return insights[:2]
