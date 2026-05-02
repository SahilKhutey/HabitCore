def generate_nudge(context):
    nudges = []

    # Rule 1: High distraction
    if context["distraction_minutes"] > 60:
        nudges.append({
            "message": "You've been distracted for a while. Take a 5-min reset.",
            "priority": 2
        })

    # Rule 2: Low focus
    if context["focus_score"] < 30:
        nudges.append({
            "message": "Start a 10-minute deep work session.",
            "priority": 3
        })

    # Rule 3: Last event scrolling
    if context["last_event"] == "scrolling":
        nudges.append({
            "message": "You're drifting. Return to your priority task.",
            "priority": 4
        })

    if not nudges:
        return {"message": "You're on track. Keep going.", "priority": 1}

    # Return highest priority nudge
    return sorted(nudges, key=lambda x: -x["priority"])[0]
