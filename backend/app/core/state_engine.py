from typing import Dict, Any, Optional
from enum import Enum

class UserMode(str, Enum):
    NORMAL = "normal"
    BURNOUT = "burnout"
    RECOVERY = "recovery"
    HYPER = "hyper"  # High engagement state

class UserStateEngine:
    def calculate_engagement_score(self, user_data: Dict[str, Any]) -> float:
        """Calculate comprehensive engagement score (0-100)"""
        streak = user_data.get('current_streak', 0)
        completion_rate = user_data.get('completion_rate', 0.0)
        session_frequency = user_data.get('session_frequency', 0)
        recent_activity = user_data.get('recent_activity', 0)
        
        # Normalized weights
        engagement_score = (
            min(streak, 30) / 30 * 30 +          # 30% weight, max 30-day streak
            completion_rate * 40 +               # 40% weight
            min(session_frequency, 7) / 7 * 20 + # 20% weight, max 7 sessions/week
            min(recent_activity, 10) / 10 * 10   # 10% weight, max 10 recent activities
        )
        
        return min(engagement_score, 100.0)
    
    def determine_user_mode(self, user_data: Dict[str, Any]) -> UserMode:
        """Determine optimal user state based on behavior patterns"""
        engagement = self.calculate_engagement_score(user_data)
        burnout_score = user_data.get('burnout_score', 0.0)
        recovery_plan_active = user_data.get('recovery_plan_active', False)
        
        if recovery_plan_active:
            return UserMode.RECOVERY
        
        if burnout_score > 0.7:
            return UserMode.BURNOUT
        
        if engagement > 80 and user_data.get('current_streak', 0) >= 14:
            return UserMode.HYPER
        
        return UserMode.NORMAL
    
    def get_state_based_actions(self, user_mode: UserMode) -> Dict[str, Any]:
        """Get actions tailored to current user state"""
        actions = {
            UserMode.NORMAL: {
                'suggest_new_habits': True,
                'challenge_level': 'medium',
                'notification_frequency': 'normal'
            },
            UserMode.BURNOUT: {
                'suggest_new_habits': False,
                'challenge_level': 'easy',
                'notification_frequency': 'low',
                'message': "Let's focus on recovery first"
            },
            UserMode.RECOVERY: {
                'suggest_new_habits': False,
                'challenge_level': 'very_easy',
                'notification_frequency': 'minimal',
                'max_habits': 2
            },
            UserMode.HYPER: {
                'suggest_new_habits': True,
                'challenge_level': 'hard',
                'notification_frequency': 'high',
                'unlock_challenges': True
            }
        }
        
        return actions.get(user_mode, actions[UserMode.NORMAL])

# Singleton instance
user_state_engine = UserStateEngine()
