"""
Nudge Templates — Behavioral intervention generation.
"""
from typing import Dict, Any

TEMPLATES = {
    "high_distraction_spike": [
        {
            "type": "interrupt",
            "message": "Focus detected slipping. Time for a 2-minute breath reset?",
            "priority": 2
        },
        {
            "type": "redirect",
            "message": "You're getting distracted. What's the one thing that matters right now?",
            "priority": 1
        }
    ],
    "active_avoidance_cycle": [
        {
            "type": "reflective",
            "message": "You've hit an avoidance loop. What are you trying to avoid feeling?",
            "priority": 3
        },
        {
            "type": "redirect",
            "message": "Avoidance cycle detected. Can you do just 2 minutes of work now?",
            "priority": 2
        }
    ],
    "low_energy_drift": [
        {
            "type": "reflective",
            "message": "Energy is low, which usually leads to avoidance. Start small.",
            "priority": 2
        }
    ]
}

def generate_nudge_content(pattern_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Selects the best template based on pattern type and priority.
    """
    options = TEMPLATES.get(pattern_type, [])
    if not options:
        return {
            "type": "generic",
            "message": "Notice your current pattern and reset.",
            "priority": 1
        }
        
    # In a real system, we'd use A/B testing or bandit algorithms here.
    # For now, we take the highest priority one.
    return sorted(options, key=lambda x: x["priority"], reverse=True)[0]
