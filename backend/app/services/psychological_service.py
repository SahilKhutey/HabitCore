from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from .cache import cached
from .ai_service import get_ai_service
import random

class PsychologicalService:
    def __init__(self):
        self.ai_service = get_ai_service()
    
    def calculate_daily_insights(self, checkin_data: Dict[str, Any], habit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized insights based on mood, energy, and habits"""
        insights = []
        
        # Mood-energy correlation
        if checkin_data.get('mood') == 'happy' and checkin_data.get('energy_morning') == 'high':
            insights.append("You're starting days with high energy and positive mood - great foundation!")
        
        # Habit-mood correlation
        completed_habits = habit_data.get('completed_today', 0)
        if completed_habits > 3 and checkin_data.get('mood') == 'happy':
            insights.append("Completing multiple habits seems to boost your mood! 🎯")
        
        # Sleep impact
        if checkin_data.get('sleep_quality', 0) <= 2 and checkin_data.get('energy_morning') == 'low':
            insights.append("Poor sleep quality might be affecting your morning energy. Consider a bedtime routine.")
        
        return {
            "insights": insights,
            "recommendations": self._generate_recommendations(checkin_data, habit_data)
        }
    
    def _generate_recommendations(self, checkin_data: Dict[str, Any], habit_data: Dict[str, Any]) -> List[str]:
        """Generate behavioral recommendations"""
        recommendations = []
        
        # Based on energy patterns
        if checkin_data.get('energy_morning') == 'high':
            recommendations.append("Schedule important habits in the morning when your energy is highest")
        elif checkin_data.get('energy_evening') == 'high':
            recommendations.append("You seem to have more energy in evenings - perfect for evening routines")
        
        # Based on current streak
        current_streak = habit_data.get('current_streak', 0)
        if current_streak >= 7:
            recommendations.append("Amazing 7-day streak! Consider adding one new easy habit to maintain momentum")
        elif current_streak == 0:
            recommendations.append("Fresh start! Try beginning with just one micro-habit to build consistency")
        
        return recommendations
    
    def determine_identity_progression(self, xp: int, streak: int, consistency_rate: float) -> str:
        """Determine user's identity level based on progress"""
        if xp >= 1000 and streak >= 30 and consistency_rate >= 0.8:
            return "elite"
        elif xp >= 500 and streak >= 14 and consistency_rate >= 0.7:
            return "disciplined"
        elif xp >= 100 and streak >= 7 and consistency_rate >= 0.6:
            return "builder"
        else:
            return "beginner"
    
    def generate_encouragement_message(self, success: bool, context: Dict[str, Any]) -> str:
        """Generate context-aware encouragement messages"""
        if success:
            messages = [
                "Amazing work! You're building powerful habits every day! 💪",
                "Consistency is key, and you're nailing it! 🎯",
                "Every completed habit brings you closer to your best self! 🌟",
                "You're not just doing habits - you're building a better life! ✨"
            ]
        else:
            messages = [
                "Tomorrow is a new opportunity to make progress! 🌅",
                "Even small steps count - you've got this! 👣",
                "Progress isn't linear. What's one tiny thing you can do right now? 🌱",
                "Remember why you started. You're capable of amazing things! 💫"
            ]
        
        return random.choice(messages)
    
    def calculate_xp_reward(self, habit_difficulty: str, streak: int) -> int:
        """Calculate XP reward based on difficulty and streak"""
        base_xp = {
            "easy": 10,
            "medium": 25,
            "hard": 50
        }
        
        streak_bonus = min(streak * 2, 50)  # Max 50 bonus for long streaks
        
        return base_xp.get(habit_difficulty, 10) + streak_bonus
    
    def detect_burnout_risk(self, habit_data: Dict[str, Any], checkin_data: Dict[str, Any]) -> bool:
        """Detect potential burnout risk"""
        failed_habits = habit_data.get('failed_recently', 0)
        low_energy_days = checkin_data.get('low_energy_days', 0)
        poor_mood_days = checkin_data.get('poor_mood_days', 0)
        
        return (failed_habits >= 5 or low_energy_days >= 3 or poor_mood_days >= 3)

# Singleton instance
psychological_service = PsychologicalService()
