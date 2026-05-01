from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import delete
from ..models.behavioral import UserBehaviorLog

class DataLifecycleManager:
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def cleanup_old_logs(self, retention_days: int = 14):
        """Clean up old behavior logs"""
        cutoff = datetime.utcnow() - timedelta(days=retention_days)
        
        # Delete old logs
        delete_stmt = delete(UserBehaviorLog).where(
            UserBehaviorLog.timestamp < cutoff
        )
        
        try:
            self.db.execute(delete_stmt)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Cleanup error: {e}")
            self.db.rollback()
            return False

    def aggregate_daily_stats(self):
        """Placeholder for daily statistics aggregation"""
        pass
