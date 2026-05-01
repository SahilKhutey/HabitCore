import random
from typing import Dict, Any
from datetime import datetime, timedelta

class AdvancedGamificationService:
    def __init__(self):
        self.mystery_rewards = [
            {"type": "xp", "value": 50, "message": "🎉 Bonus XP!"},
            {"type": "coins", "value": 25, "message": "💰 Coin shower!"},
            {"type": "streak", "value": 1, "message": "🔥 Streak shield!"},
            {"type": "badge", "value": "lucky", "message": "🍀 Lucky day badge!"}
        ]
        
        self.streak_tension_messages = [
            "⏰ Only {time_left} to save your {streak}-day streak!",
            "⚠️ Don't let your {streak}-day streak slip away!",
            "🔔 {time_left} remaining - you've got this!",
            "🎯 So close! Just {time_left} to keep your streak alive!"
        ]
    
    def generate_mystery_reward(self) -> Dict[str, Any]:
        """Generate variable mystery reward"""
        reward = random.choice(self.mystery_rewards)
        return {
            **reward,
            'reveal_animation': True,
            'anticipation_message': "What could it be? 🎁"
        }
    
    def get_streak_tension_message(self, streak: int, time_left: str) -> str:
        """Generate streak tension message"""
        message = random.choice(self.streak_tension_messages)
        return message.format(streak=streak, time_left=time_left)
    
    def calculate_time_until_streak_loss(self, last_activity: datetime) -> str:
        """Calculate time until streak loss"""
        deadline = last_activity + timedelta(days=1)
        time_left = deadline - datetime.utcnow()
        
        if time_left.total_seconds() <= 0:
            return "0h 0m"
        
        hours = int(time_left.total_seconds() / 3600)
        minutes = int((time_left.total_seconds() % 3600) / 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def create_anticipation_loop(self, user_progress: Dict[str, Any]) -> Dict[str, Any]:
        """Create anticipation for next reward"""
        xp = user_progress.get('xp', 0)
        next_milestone = self._get_next_milestone(xp)
        habits_to_milestone = max(1, (next_milestone - xp) // 10)
        
        return {
            'next_milestone': next_milestone,
            'habits_needed': habits_to_milestone,
            'message': f"Complete {habits_to_milestone} more habits for a milestone reward!",
            'progress_percentage': (xp % 100) / 100 * 100
        }
    
    def _get_next_milestone(self, current_xp: int) -> int:
        """Get next milestone XP"""
        milestones = [100, 250, 500, 1000, 2500, 5000]
        for milestone in milestones:
            if current_xp < milestone:
                return milestone
        return ((current_xp // 1000) + 1) * 1000

# Singleton instance
gamification_service = AdvancedGamificationService()
