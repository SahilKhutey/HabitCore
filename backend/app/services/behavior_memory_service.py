from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.behavioral import BehaviorPattern, UserBehaviorLog, RecoveryPlan

class BehaviorMemoryService:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def log_behavior(self, user_id: str, event_type: str, event_data: Dict, context: Dict = None):
        """Log user behavior for pattern analysis"""
        log = UserBehaviorLog(
            user_id=user_id,
            event_type=event_type,
            event_data=event_data,
            context=context or {}
        )
        self.db.add(log)
        self.db.commit()
    
    def analyze_time_patterns(self, user_id: str) -> List[BehaviorPattern]:
        """Analyze when user is most successful with habits"""
        logs = self.db.query(UserBehaviorLog).filter(
            UserBehaviorLog.user_id == user_id,
            UserBehaviorLog.event_type == 'habit_completed'
        ).all()
        
        time_slots = {}
        for log in logs:
            hour = log.timestamp.hour
            time_slots[hour] = time_slots.get(hour, 0) + 1
        
        if time_slots:
            best_hour = max(time_slots.items(), key=lambda x: x[1])[0]
            confidence = time_slots[best_hour] / len(logs)
            
            pattern = self.db.query(BehaviorPattern).filter_by(
                user_id=user_id, 
                insight_key="best_time"
            ).first()
            
            if not pattern:
                pattern = BehaviorPattern(user_id=user_id, pattern_type="time_preference", insight_key="best_time")
                self.db.add(pattern)
            
            pattern.insight_value = f"{best_hour}:00"
            pattern.confidence_score = confidence
            pattern.metadata_json = {"distribution": time_slots}
            pattern.last_updated = datetime.utcnow()
            
            self.db.commit()
            return [pattern]
        
        return []
    
    def analyze_day_patterns(self, user_id: str) -> List[BehaviorPattern]:
        """Analyze which days user struggles most"""
        logs = self.db.query(UserBehaviorLog).filter(
            UserBehaviorLog.user_id == user_id,
            UserBehaviorLog.event_type.in_(['habit_completed', 'habit_failed'])
        ).all()
        
        day_success = {}
        day_attempts = {}
        
        for log in logs:
            day = log.timestamp.strftime('%A')
            success = log.event_data.get('completed', False)
            
            day_attempts[day] = day_attempts.get(day, 0) + 1
            if success:
                day_success[day] = day_success.get(day, 0) + 1
        
        worst_day = None
        worst_ratio = 1.0
        
        for day, attempts in day_attempts.items():
            successes = day_success.get(day, 0)
            success_ratio = successes / attempts if attempts > 0 else 0
            
            if success_ratio < worst_ratio:
                worst_ratio = success_ratio
                worst_day = day
        
        if worst_day and worst_ratio < 0.5:  # Less than 50% success
            pattern = self.db.query(BehaviorPattern).filter_by(
                user_id=user_id, 
                insight_key="worst_day"
            ).first()
            
            if not pattern:
                pattern = BehaviorPattern(user_id=user_id, pattern_type="day_pattern", insight_key="worst_day")
                self.db.add(pattern)
                
            pattern.insight_value = worst_day
            pattern.confidence_score = 1.0 - worst_ratio
            pattern.metadata_json = {"success_rate": worst_ratio}
            pattern.last_updated = datetime.utcnow()
            
            self.db.commit()
            return [pattern]
        
        return []
    
    def get_user_patterns(self, user_id: str) -> Dict[str, Any]:
        """Get all behavioral patterns for a user"""
        patterns = self.db.query(BehaviorPattern).filter(
            BehaviorPattern.user_id == user_id
        ).all()
        
        return {
            pattern.insight_key: {
                "value": pattern.insight_value,
                "confidence": pattern.confidence_score,
                "metadata": pattern.metadata_json
            }
            for pattern in patterns
        }
    
    def calculate_burnout_score(self, user_id: str, days: int = 7) -> float:
        """Calculate comprehensive burnout risk score"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Get recent logs
        logs = self.db.query(UserBehaviorLog).filter(
            UserBehaviorLog.user_id == user_id,
            UserBehaviorLog.timestamp >= cutoff
        ).all()
        
        failed_habits = sum(1 for log in logs 
                          if log.event_type == 'habit_completed' 
                          and not log.event_data.get('completed', False))
        
        low_energy_days = sum(1 for log in logs 
                             if log.event_type == 'checkin'
                             and log.event_data.get('energy_morning') == 'low')
        
        poor_mood_days = sum(1 for log in logs 
                            if log.event_type == 'checkin'
                            and log.event_data.get('mood') in ['sad', 'angry', 'tired'])
        
        checkin_logs = [log for log in logs if log.event_type == 'checkin']
        total_days = len(set(log.timestamp.date() for log in checkin_logs))
        
        if total_days == 0:
            return 0.0
        
        burnout_score = (
            (failed_habits / max(1, len(logs)) * 0.4) +
            (low_energy_days / total_days * 0.3) +
            (poor_mood_days / total_days * 0.3)
        )
        
        return min(burnout_score, 1.0)
    
    def create_recovery_plan(self, user_id: str, trigger_type: str) -> Optional[RecoveryPlan]:
        """Create personalized recovery plan"""
        burnout_score = self.calculate_burnout_score(user_id)
        
        if burnout_score > 0.7:
            plan = RecoveryPlan(
                user_id=user_id,
                trigger_type=trigger_type,
                plan_type="habit_reduction",
                actions={
                    "message": "You're pushing too hard. Reduce your habit load by 50% for 3 days.",
                    "suggestions": [
                        "Focus on just 1-2 core habits",
                        "Take 10-minute breaks between tasks",
                        "Practice deep breathing exercises"
                    ]
                },
                expires_at=datetime.utcnow() + timedelta(days=3)
            )
            self.db.add(plan)
            self.db.commit()
            return plan
        
        return None
