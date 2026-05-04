import random
from typing import Dict, Any, List
from datetime import datetime, timedelta, timezone

class RecoveryService:
    def __init__(self):
        self.recovery_strategies = {
            'burnout': [
                {
                    'action': 'reduce_habits',
                    'message': "Let's reduce your habit load by 50% for 3 days",
                    'duration': 3
                },
                {
                    'action': 'micro_habits',
                    'message': "Try 2-minute versions of your habits today",
                    'duration': 1
                }
            ],
            'failure_streak': [
                {
                    'action': 'habit_size',
                    'message': "Reduce habit size to build momentum",
                    'duration': 2
                },
                {
                    'action': 'accountability',
                    'message': "Share your goal with a friend for accountability",
                    'duration': 7
                }
            ],
            'low_mood': [
                {
                    'action': 'self_compassion',
                    'message': "Practice self-compassion - tomorrow is a new day",
                    'duration': 1
                },
                {
                    'action': 'tiny_win',
                    'message': "Focus on one tiny win today to build momentum",
                    'duration': 1
                }
            ]
        }
    
    def generate_recovery_plan(self, trigger_type: str, severity: float) -> Dict[str, Any]:
        """Generate personalized recovery plan"""
        strategies = self.recovery_strategies.get(trigger_type, [])
        
        if not strategies:
            return {
                'action': 'general_rest',
                'message': "Take today as a rest day and come back refreshed tomorrow",
                'duration': 1
            }
        
        # Select strategy based on severity
        strategy = strategies[0] if severity > 0.7 else strategies[-1]
        
        return {
            **strategy,
            'severity': severity,
            'created_at': datetime.now(timezone.utc).isoformat(),
            'expires_at': (datetime.now(timezone.utc) + timedelta(days=strategy['duration'])).isoformat()
        }
    
    def get_failure_recovery_message(self, failed_habit: str, streak: int) -> str:
        """Get encouraging message for habit failure"""
        messages = [
            f"Everyone misses sometimes. What's one tiny step you can take for '{failed_habit}' tomorrow?",
            f"Your {streak}-day streak was amazing! Now let's start a new one.",
            f"Progress isn't linear. What did you learn from today that can help tomorrow?",
            f"Tomorrow is a fresh start. Maybe try a 2-minute version of '{failed_habit}'?"
        ]
        return random.choice(messages)

# Singleton instance
recovery_service = RecoveryService()
