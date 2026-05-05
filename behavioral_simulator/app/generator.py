import json
import logging
import asyncio
import time
import random
import requests
from typing import List, Dict, Optional
from .archetypes import User, UserArchetype

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.tokens: Dict[str, str] = {} # user_id -> token

    def authenticate_user(self, user: User):
        """Register or Login user to get JWT."""
        email = f"{user.user_id}@simulator.com"
        password = "sim_password_123"
        
        try:
            # Try login
            resp = requests.post(f"{self.base_url}/auth/login", json={"email": email, "password": password}, timeout=5)
            if resp.status_code == 200:
                self.tokens[user.user_id] = resp.json()["access_token"]
                return True
            
            # If login fails, try register
            resp = requests.post(f"{self.base_url}/auth/register", json={
                "email": email, 
                "password": password,
                "full_name": f"Simulated {user.archetype.value}"
            }, timeout=5)
            
            if resp.status_code == 200:
                # Login after register
                resp = requests.post(f"{self.base_url}/auth/login", json={"email": email, "password": password}, timeout=5)
                if resp.status_code == 200:
                    self.tokens[user.user_id] = resp.json()["access_token"]
                    return True
        except Exception as e:
            logger.error(f"Auth failed for {user.user_id}: {e}")
        return False

    def send_event(self, user_id: str, event_data: dict):
        token = self.tokens.get(user_id)
        if not token:
            return False
            
        headers = {"Authorization": f"Bearer {token}"}
        
        # Map simulator event to Backend Intelligence Event
        # Simulator Types: reflection, habit_complete, mood_check, pattern_detected
        sim_type = event_data.get("event_type")
        
        mapping = {
            "reflection": ("habit_completed", "cognitive"), # Close enough for nudge trigger
            "habit_complete": ("habit_completed", "behavior"),
            "mood_check": ("habit_completed", "behavior"), # Use habit_completed to trigger nudge logic
            "pattern_detected": ("app_open", "system")
        }
        
        target_type, target_cat = mapping.get(sim_type, ("habit_completed", "behavior"))
        
        payload = {
            "event_type": target_type,
            "category": target_cat,
            "value": event_data.get("urgency_score", 1.0),
            "metadata": {
                "sim_id": event_data.get("event_id"),
                "archetype": event_data.get("archetype"),
                "original_type": sim_type,
                "content": event_data.get("content")
            }
        }
        
        try:
            resp = requests.post(f"{self.base_url}/intelligence/event", json=payload, headers=headers, timeout=5)
            return resp.status_code == 200
        except Exception as e:
            logger.error(f"Event post failed for {user_id}: {e}")
            return False

class EventGenerator:
    def __init__(self, api_url: str, user_count: int = 20):
        self.api = APIClient(api_url)
        self.users = self._initialize_users(user_count)
        self.is_running = False
        self.event_rate_multiplier = 1.0
        self.stats = {"sent": 0, "failed": 0}

    def _initialize_users(self, count: int) -> List[User]:
        users = []
        archetypes = list(UserArchetype)
        for i in range(count):
            arch = random.choice(archetypes)
            is_premium = random.random() < 0.2
            users.append(User(user_id=f"sim_v2_{i}", archetype=arch, is_premium=is_premium))
        return users

    async def run(self, duration_sec: int = 0):
        self.is_running = True
        start_time = time.time()
        
        logger.info(f"Authenticating {len(self.users)} simulated users...")
        for user in self.users:
            if self.api.authenticate_user(user):
                logger.info(f"Authenticated {user.user_id} ({user.archetype.value})")
            else:
                logger.warning(f"Failed to auth {user.user_id}")

        logger.info(f"Starting API stress test for {len(self.users)} users")
        
        while self.is_running:
            if duration_sec > 0 and (time.time() - start_time) > duration_sec:
                break
                
            tasks = []
            for user in self.users:
                event = user.generate_event()
                if event:
                    if self.event_rate_multiplier > 1.0:
                        extra = int(self.event_rate_multiplier)
                        for _ in range(extra):
                            tasks.append(self.send_api_event(user.user_id, event))
                    else:
                        if random.random() < self.event_rate_multiplier:
                            tasks.append(self.send_api_event(user.user_id, event))
            
            if tasks:
                await asyncio.gather(*tasks)
            
            await asyncio.sleep(0.5) # Throttle simulator ticks
            
        logger.info(f"Simulation stopped. Stats: {self.stats}")

    async def send_api_event(self, user_id: str, event: dict):
        # Run synchronous request in thread pool
        loop = asyncio.get_event_loop()
        success = await loop.run_in_executor(None, self.api.send_event, user_id, event)
        if success:
            self.stats["sent"] += 1
        else:
            self.stats["failed"] += 1

    def stop(self):
        self.is_running = False

    def set_scenario_params(self, archetype_override: UserArchetype = None, multiplier: float = 1.0):
        self.event_rate_multiplier = multiplier
        if archetype_override:
            for user in self.users:
                user.archetype = archetype_override
