from datetime import date, timedelta

def calculate_streak(logs):
    if not logs:
        return 0

    # Ensure unique dates (handle multiple completions in one day)
    log_dates = sorted(
        {log.date for log in logs},
        reverse=True
    )

    streak = 0
    today = date.today()

    # If the most recent log isn't today or yesterday, streak is broken
    if log_dates[0] < today - timedelta(days=1):
        return 0

    # Determine our starting point for the iteration
    # If they already did it today, start checking from today
    # If they did it yesterday but not today, start checking from yesterday
    current_check_date = today if log_dates[0] == today else (today - timedelta(days=1))

    for log_date in log_dates:
        if log_date == current_check_date:
            streak += 1
            current_check_date -= timedelta(days=1)
        elif log_date > current_check_date:
            continue # Skip multiple logs on the same day (though already handled by set)
        else:
            break # Gap found

    return streak

def calculate_completion_rate(logs, days=7):
    if not logs: return 0
    today = date.today()
    week_ago = today - timedelta(days=days)
    
    unique_days = len({log.date for log in logs if log.date >= week_ago})
    return unique_days / days

def adjust_habit_difficulty(habit, logs):
    rate = calculate_completion_rate(logs)
    
    if rate > 0.8:
        if habit.difficulty == "easy":
            habit.difficulty = "medium"
            habit.target_per_day += 1
        elif habit.difficulty == "medium":
            habit.difficulty = "hard"
            habit.target_per_day += 1
        return "increase"
    elif rate < 0.4:
        if habit.difficulty == "hard":
            habit.difficulty = "medium"
            habit.target_per_day = max(1, habit.target_per_day - 1)
        elif habit.difficulty == "medium":
            habit.difficulty = "easy"
            habit.target_per_day = 1
        return "decrease"
    
    return None
