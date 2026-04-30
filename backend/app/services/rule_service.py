from sqlalchemy.orm import Session
from app.models.user import User
from app.models.user_preferences import UserRule

class RuleService:
    @staticmethod
    def process_rules(db: Session, user: User, event: str):
        rules = db.query(UserRule).filter(UserRule.user_id == user.id, UserRule.is_active == True).all()
        
        results = []
        for rule in rules:
            if rule.condition == "miss_2_days" and event == "missed":
                # Logic to reset streak would go here
                results.append({"action": rule.action, "triggered": True})
                
            if rule.condition == "complete_all_habits" and event == "all_completed":
                user.xp += 50
                results.append({"action": "bonus_xp", "value": 50})
        
        if results:
            db.commit()
            
        return results
