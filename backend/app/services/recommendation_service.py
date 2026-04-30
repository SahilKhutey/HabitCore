from app.models.user import User

class RecommendationService:
    @staticmethod
    def get_recommendations(user: User):
        # Identity-based recommendations
        if user.identity_goal == "Fit":
            return [
                {"title": "Drink Water", "difficulty": "Easy"},
                {"title": "10 min Morning Stretch", "difficulty": "Medium"},
                {"title": "Walk 5,000 steps", "difficulty": "Hard"}
            ]
            
        if user.identity_goal == "Productive":
            return [
                {"title": "Plan Tomorrow", "difficulty": "Easy"},
                {"title": "Deep Work (1 hour)", "difficulty": "Hard"},
                {"title": "Clear Inbox", "difficulty": "Medium"}
            ]

        if user.identity_goal == "Calm":
            return [
                {"title": "Breathe (5 min)", "difficulty": "Easy"},
                {"title": "Daily Journal", "difficulty": "Medium"},
                {"title": "No Screens before bed", "difficulty": "Hard"}
            ]

        # Default fallback
        return [
            {"title": "Read 10 pages", "difficulty": "Medium"},
            {"title": "Drink Water", "difficulty": "Easy"}
        ]
