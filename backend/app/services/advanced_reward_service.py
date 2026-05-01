import random
from typing import Dict, Any
from datetime import datetime, timedelta

class AdvancedRewardService:
    def __init__(self):
        self.variable_rewards = {
            'small': [0, 5, 10, 15],
            'medium': [10, 15, 20, 25],
            'large': [25, 30, 40, 50]
        }
        
        self.identity_messages = {
            'beginner': [
                "You're starting strong! Every journey begins with a single step.",
                "Welcome to your habit-building journey! You've got this."
            ],
            'builder': [
                "You're building consistency! Those small actions add up.",
                "Your dedication is showing. Keep building momentum!"
            ],
            'disciplined': [
                "You're developing real discipline! This is where habits stick.",
                "Your consistency is impressive. You're becoming unstoppable!"
            ],
            'elite': [
                "Elite level! You've mastered the art of habit formation.",
                "You're in the top tier of habit builders. Inspire others!"
            ]
        }
    
    def calculate_xp_with_consistency(self, base_xp: int, streak: int, 
                                    difficulty: str, consistency_rate: float) -> int:
        """Calculate XP with consistency multiplier"""
        consistency_multiplier = min(1.0 + (streak * 0.1) + (consistency_rate * 0.5), 2.0)
        difficulty_bonus = {
            'easy': 1.0,
            'medium': 1.5,
            'hard': 2.0
        }.get(difficulty, 1.0)
        
        return int(base_xp * consistency_multiplier * difficulty_bonus)
    
    def get_variable_reward(self, reward_size: str = 'small') -> int:
        """Get variable reward for dopamine effect"""
        return random.choice(self.variable_rewards[reward_size])
    
    def get_identity_message(self, identity_level: str, current_streak: int) -> str:
        """Get identity-reinforcing message"""
        messages = self.identity_messages.get(identity_level, 'beginner')
        if not isinstance(messages, list):
             messages = self.identity_messages.get('beginner')
             
        message = random.choice(messages)
        if current_streak >= 7:
            message += f" Your {current_streak}-day streak is amazing!"
        return message
    
    def generate_milestone_message(self, xp: int, next_milestone: int) -> str:
        """Generate progress milestone message"""
        xp_needed = next_milestone - xp
        if xp_needed <= 50 and xp_needed > 0:
            return f"Only {xp_needed} XP until your next milestone! 🎯"
        return None
    
    def check_unlockables(self, level: int) -> Dict[str, Any]:
        """Check for new feature unlocks"""
        unlocks = {
            5: {"feature": "advanced_analytics", "message": "Unlocked Advanced Analytics! 📊"},
            10: {"feature": "ai_coach", "message": "Unlocked AI Coach! 🤖"},
            15: {"feature": "custom_themes", "message": "Unlocked Custom Themes! 🎨"},
            20: {"feature": "group_challenges", "message": "Unlocked Group Challenges! 👥"}
        }
        
        return unlocks.get(level, {})

# Singleton instance
advanced_reward_service = AdvancedRewardService()
