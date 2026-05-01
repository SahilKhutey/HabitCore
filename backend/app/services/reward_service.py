from typing import Dict, Any, List
import random
from datetime import datetime

class RewardService:
    def __init__(self):
        self.badges = {
            "first_habit": {"name": "First Step", "xp_required": 10},
            "weekly_warrior": {"name": "Weekly Warrior", "xp_required": 100},
            "monthly_master": {"name": "Monthly Master", "xp_required": 500},
            "streak_saver": {"name": "Streak Saver", "xp_required": 200},
            "habit_hero": {"name": "Habit Hero", "xp_required": 1000}
        }
    
    def calculate_level_up(self, current_xp: int, current_level: int) -> Dict[str, Any]:
        """Calculate if user levels up and provide rewards"""
        levels = {
            1: 0, 2: 100, 3: 250, 4: 500, 5: 1000,
            6: 1500, 7: 2000, 8: 3000, 9: 4000, 10: 5000
        }
        
        new_level = 1
        for level, xp_required in levels.items():
            if current_xp >= xp_required:
                new_level = level
        
        level_up = new_level > current_level
        
        if level_up:
            reward = {
                "coins": new_level * 50,
                "new_badges": self._check_badges(current_xp),
                "unlocked_features": self._get_unlocked_features(new_level)
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
    
    def _get_unlocked_features(self, level: int) -> List[str]:
        """Get features unlocked at each level"""
        unlocks = {
            3: ["advanced_analytics", "custom_themes"],
            5: ["ai_coach", "habit_challenges"],
            7: ["group_quests", "premium_content"],
            10: ["master_level", "all_features"]
        }
        return unlocks.get(level, [])
    
    def generate_daily_challenge(self) -> Dict[str, Any]:
        """Generate a random daily challenge"""
        challenges = [
            {
                "name": "Morning Momentum",
                "description": "Complete 3 habits before noon",
                "reward": 30,
                "type": "xp"
            },
            {
                "name": "Consistency King",
                "description": "Maintain your streak for 3 more days",
                "reward": 50,
                "type": "xp"
            },
            {
                "name": "Energy Boost",
                "description": "Complete a habit during your low-energy time",
                "reward": 25,
                "type": "coins"
            }
        ]
        return random.choice(challenges)

# Singleton instance
reward_service = RewardService()
