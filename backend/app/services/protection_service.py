from datetime import date, timedelta
from typing import Set

class ProtectionService:
    @staticmethod
    def missed_yesterday(log_dates: Set[date]) -> bool:
        """Checks if the user missed a log yesterday."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        return yesterday not in log_dates

    @staticmethod
    def apply_streak_freeze(user, log_dates: Set[date]) -> bool:
        """
        Attempts to apply a streak freeze if the user missed yesterday.
        Returns True if a freeze was applied, False otherwise.
        """
        if user.streak_freeze <= 0:
            return False

        if ProtectionService.missed_yesterday(log_dates):
            user.streak_freeze -= 1
            return True

        return False

    @staticmethod
    def recovery_streak(old_streak: int) -> int:
        """Calculates the recovered streak value (half of old streak)."""
        return max(1, old_streak // 2)

    @staticmethod
    def detect_burnout(logs, app_opens: int = None) -> bool:
        """
        Detects burnout based on completion rate in the last 7 days.
        """
        if not logs:
            return False
            
        today = date.today()
        seven_days_ago = today - timedelta(days=7)
        
        last_7_days_logs = [log for log in logs if log.date >= seven_days_ago]
        unique_dates = {log.date for log in last_7_days_logs}
        
        completion_rate = len(unique_dates) / 7
        
        # Burnout signal: completion rate below 30%
        if completion_rate < 0.3:
            return True
            
        return False
