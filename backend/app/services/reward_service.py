import random
from typing import Dict, Any, List
from datetime import datetime, timedelta

class RewardService:
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

        self.badges = {
            "first_habit": {"name": "First Step", "xp_required": 10},
            "weekly_warrior": {"name": "Weekly Warrior", "xp_required": 100},
            "monthly_master": {"name": "Monthly Master", "xp_required": 500},
            "streak_saver": {"name": "Streak Saver", "xp_required": 200},
            "habit_hero": {"name": "Habit Hero", "xp_required": 1000}
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
        messages = self.identity_messages.get(identity_level, self.identity_messages['beginner'])
        message = random.choice(messages)
        if current_streak >= 7:
            message += f" Your {current_streak}-day streak is amazing!"
        return message

    def calculate_level_up(self, current_xp: int, current_level: int) -> Dict[str, Any]:
        """Calculate if user levels up and provide rewards"""
        # Linear progression for early levels, then exponential
        def xp_for_level(lvl):
            if lvl <= 1: return 0
            return int(100 * (lvl ** 1.5))

        new_level = current_level
        while current_xp >= xp_for_level(new_level + 1):
            new_level += 1
        
        level_up = new_level > current_level
        
        if level_up:
            reward = {
                "coins": new_level * 50,
                "new_badges": self._check_badges(current_xp),
                "unlocked_features": self.check_unlockables(new_level)
            }
        else:
            reward = {}
        
        return {
            "level": new_level,
            "level_up": level_up,
            "reward": reward
        }

    def _check_badges(self, xp: int) -> List[str]:
        """Check which badges user qualifies for"""
        earned_badges = []
        for badge_id, criteria in self.badges.items():
            if xp >= criteria["xp_required"]:
                earned_badges.append(badge_id)
        return earned_badges
    
    def check_unlockables(self, level: int) -> Dict[str, Any]:
        """Check for new feature unlocks"""
        unlocks = {
            5: {"feature": "advanced_analytics", "message": "Unlocked Advanced Analytics! 📊"},
            10: {"feature": "ai_coach", "message": "Unlocked AI Coach! 🤖"},
            15: {"feature": "custom_themes", "message": "Unlocked Custom Themes! 🎨"},
            20: {"feature": "group_challenges", "message": "Unlocked Group Challenges! 👥"}
        }
        return unlocks.get(level, {})

    def generate_daily_challenge(self) -> Dict[str, Any]:
        """Generate a random daily challenge"""
        challenges = [
            {"name": "Morning Momentum", "description": "Complete 3 habits before noon", "reward": 30, "type": "xp"},
            {"name": "Consistency King", "description": "Maintain your streak for 3 more days", "reward": 50, "type": "xp"},
            {"name": "Energy Boost", "description": "Complete a habit during your low-energy time", "reward": 25, "type": "coins"}
        ]
        return random.choice(challenges)

    def adjust_habit_difficulty(self, habit, logs):
        """
        Dynamically adjust habit difficulty based on performance history.
        - Harder if completion rate is > 90% over last 7 completions.
        - Easier if completion rate is < 30%.
        """
        if len(logs) < 7: return None
        
        last_7 = logs[-7:]
        completion_count = sum(1 for log in last_7 if log.status == "completed")
        rate = completion_count / 7

        old_difficulty = habit.difficulty
        if rate > 0.9:
            if habit.difficulty == "easy": habit.difficulty = "medium"
            elif habit.difficulty == "medium": habit.difficulty = "hard"
        elif rate < 0.3:
            if habit.difficulty == "hard": habit.difficulty = "medium"
            elif habit.difficulty == "medium": habit.difficulty = "easy"
            
        return habit.difficulty if habit.difficulty != old_difficulty else None

# Singleton instance
reward_service = RewardService()
