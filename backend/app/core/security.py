from typing import Dict, Any, Optional
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

class SecurityEngine:
    def __init__(self):
        self.event_counters = defaultdict(lambda: defaultdict(int))
        self.last_reset = datetime.now()
    
    def validate_event(self, user_id: str, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Validate event for security and abuse prevention"""
        # Rate limiting
        if not self._check_rate_limit(user_id, event_type):
            return False
        
        # Data validation
        if not self._validate_event_data(event_type, event_data):
            return False
        
        # XP farming prevention (simplified)
        if event_type == 'habit_completed' and event_data.get('xp_earned', 0) > 200:
            return False
        
        return True
    
    def reset(self):
        """Reset counters for testing"""
        self.event_counters.clear()
        self.last_reset = datetime.now()

    def _check_rate_limit(self, user_id: str, event_type: str) -> bool:
        """Check rate limits for events"""
        now = datetime.now()
        current_minute = now.minute
        
        # Reset counter if minute changed
        if now - self.last_reset > timedelta(minutes=1):
            self.event_counters.clear()
            self.last_reset = now
        
        key = f"{user_id}_{event_type}"
        self.event_counters[current_minute][key] += 1
        
        # Different rate limits for different event types
        limits = {
            'habit_completed': 30,  # 30 habits per minute
            'checkin': 5,           # 5 checkins per minute
            'general': 60           # 60 events per minute
        }
        
        limit = limits.get(event_type, limits['general'])
        return self.event_counters[current_minute][key] <= limit
    
    def _validate_event_data(self, event_type: str, event_data: Dict[str, Any]) -> bool:
        """Validate event data structure"""
        if event_type == 'habit_completed':
            return 'habit_id' in event_data and 'completed' in event_data
        
        if event_type == 'checkin':
            required = ['mood', 'energy_morning', 'sleep_quality']
            return all(field in event_data for field in required)
            
        return True

# Singleton instance
security_engine = SecurityEngine()
