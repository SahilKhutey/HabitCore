import random
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any

class UserArchetype(str, Enum):
    STREAK = "streak"      # Consistent, reliable, low urgency
    DROPOFF = "dropoff"    # High urgency signals, infrequent
    BINGE = "binge"        # Bursty, high frequency
    REFLECTIVE = "reflective" # Moderate frequency, rich text

class User:
    def __init__(self, user_id: str, archetype: UserArchetype, is_premium: bool = False):
        self.user_id = user_id
        self.archetype = archetype
        self.is_premium = is_premium
        self.streak_count = random.randint(0, 100) if archetype == UserArchetype.STREAK else 0
        self.last_event_time = datetime.now(timezone.utc)

    def generate_event(self) -> Optional[Dict[str, Any]]:
        """Generates a realistic event based on archetype probability."""
        prob = self._get_probability()
        if random.random() > prob:
            return None

        event_type = self._get_event_type()
        urgency = self._get_urgency()
        content = self._get_content(event_type)
        
        event = {
            "event_id": str(uuid.uuid4()),
            "user_id": self.user_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "archetype": self.archetype.value,
            "is_premium": self.is_premium,
            "event_type": event_type,
            "urgency_score": urgency,
            "content": content,
            "metadata": {
                "streak": self.streak_count,
                "platform": random.choice(["ios", "android", "web"]),
                "version": "2.4.0"
            }
        }
        
        if self.archetype == UserArchetype.STREAK:
            self.streak_count += 1
            
        return event

    def _get_probability(self) -> float:
        """Frequency of events per tick."""
        base_probs = {
            UserArchetype.STREAK: 0.15,
            UserArchetype.DROPOFF: 0.02,
            UserArchetype.BINGE: 0.6,
            UserArchetype.REFLECTIVE: 0.1
        }
        return base_probs.get(self.archetype, 0.1)

    def _get_urgency(self) -> float:
        """Urgency score (0.0 to 1.0)."""
        if self.archetype == UserArchetype.DROPOFF:
            return random.uniform(0.7, 1.0)
        if self.archetype == UserArchetype.BINGE:
            return random.uniform(0.4, 0.8)
        return random.uniform(0.1, 0.4)

    def _get_event_type(self) -> str:
        types = ["reflection", "habit_complete", "mood_check", "pattern_detected"]
        weights = [0.4, 0.3, 0.2, 0.1]
        if self.archetype == UserArchetype.REFLECTIVE:
            weights = [0.8, 0.05, 0.1, 0.05]
        return random.choices(types, weights=weights)[0]

    def _get_content(self, event_type: str) -> str:
        reflections = [
            "Feeling a bit overwhelmed today, but pushed through.",
            "I noticed I'm more productive in the morning.",
            "Missed my workout, feeling guilty.",
            "Today was a breakthrough! Managed my stress well.",
            "Struggling with focus during the afternoon slump."
        ]
        if event_type == "reflection":
            return random.choice(reflections)
        return f"User performed {event_type}"
