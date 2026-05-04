import random
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.habit import Habit
from app.services.analytics_service import AnalyticsService
from datetime import datetime, timezone

class NudgeEngine:
    PHASE_TEMPLATES = {
        'hook': [
            "Your brain is forming a new pathway. Complete {habit} for a quick dopamine win!",
            "Day {day}: Small wins lead to big shifts. Activate {habit} now.",
            "The first few days are about neurological mapping. Don't skip {habit}!"
        ],
        'awareness': [
            "Observation: Your energy peaks after {habit}. Keep the data flowing.",
            "Pattern detected: You usually do {habit} by now. Seeing a pattern?",
            "Awareness is the first step to mastery. Check in on your {habit}."
        ],
        'intervention': [
            "Resilience check: Life is busy, but a '{identity}' doesn't negotiate with {habit}.",
            "This is the friction point. Breaking this loop is where the change happens.",
            "Intervene on your old self. Complete {habit} to prove you're in control."
        ],
        'identity': [
            "Evidence of a new you: You've done {habit} consistently. You ARE a '{identity}'.",
            "This isn't a habit anymore, it's who you are. Keep embodying the '{identity}'.",
            "Your identity as a '{identity}' is now 80% solidified. Finish {habit} to lock it in."
        ]
    }

    @staticmethod
    def get_user_phase(user: User) -> str:
        streak = user.current_streak or 0
        if streak <= 2: return 'hook'
        if streak <= 7: return 'awareness'
        if streak <= 14: return 'intervention'
        return 'identity'

    @staticmethod
    def generate_nudge(user: User, habit: Habit) -> str:
        phase = NudgeEngine.get_user_phase(user)
        templates = NudgeEngine.PHASE_TEMPLATES.get(phase, NudgeEngine.PHASE_TEMPLATES['hook'])
        
        template = random.choice(templates)
        return template.format(
            habit=habit.name,
            identity=user.identity_goal or "Hero",
            day=user.current_streak or 1
        )

    @staticmethod
    def process_nudges(db: Session):
        """
        Identifies users needing a nudge and logs events.
        """
        # Logic to find users who haven't completed their daily rituals yet
        # For simplicity in this iteration, we look for 'sliding' habits
        # (habits not marked 'done' today)
        from app.models.habit import Habit
        
        pending_habits = db.query(Habit).filter(Habit.done == False).all()
        nudges_sent = 0
        
        for habit in pending_habits:
            user = db.query(User).filter(User.id == habit.user_id).first()
            if not user: continue
            
            message = NudgeEngine.generate_nudge(user, habit)
            
            AnalyticsService.log_event(db, user.id, "nudge_generated", {
                "habit_id": str(habit.id),
                "message": message,
                "phase": NudgeEngine.get_user_phase(user),
                "identity": user.identity_goal
            })
            nudges_sent += 1
            
        return nudges_sent
