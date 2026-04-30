from app.models.user import User

class AdaptiveService:
    @staticmethod
    def get_adaptive_mode(user: User):
        # Motivation Mode: Low streak, needs encouragement
        if user.streak < 2:
            return "motivation_mode"
        
        # Challenge Mode: High streak, needs harder goals to avoid boredom
        if user.streak >= 7:
            return "challenge_mode"
            
        # Normal Mode
        return "normal"

    @staticmethod
    def get_adaptive_theme_overrides(user: User):
        mode = AdaptiveService.get_adaptive_mode(user)
        
        if mode == "motivation_mode":
            return {"primary_color": "#22c55e", "show_encouragement": True}
        
        if mode == "challenge_mode":
            return {"primary_color": "#ef4444", "harder_quests": True}
            
        return {}
