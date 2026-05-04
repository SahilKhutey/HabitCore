import json
import logging
import asyncio
import time
import random
from typing import List
from kafka import KafkaProducer
from .archetypes import User, UserArchetype

logger = logging.getLogger(__name__)

class EventGenerator:
    def __init__(self, bootstrap_servers: str, topic: str, user_count: int = 100):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all'
        )
        self.topic = topic
        self.users = self._initialize_users(user_count)
        self.is_running = False
        self.event_rate_multiplier = 1.0

    def _initialize_users(self, count: int) -> List[User]:
        users = []
        archetypes = list(UserArchetype)
        for i in range(count):
            arch = random.choice(archetypes)
            # 20% premium users
            is_premium = random.random() < 0.2
            users.append(User(user_id=f"sim_user_{i}", archetype=arch, is_premium=is_premium))
        return users

    async def run(self, duration_sec: int = 0):
        self.is_running = True
        start_time = time.time()
        
        logger.info(f"Starting event generation for {len(self.users)} users on topic {self.topic}")
        
        while self.is_running:
            if duration_sec > 0 and (time.time() - start_time) > duration_sec:
                break
                
            for user in self.users:
                # Adjust probability based on global multiplier
                event = user.generate_event()
                if event:
                    # Apply multiplier logic: if random() < multiplier, send. 
                    # If multiplier > 1, send multiple times? No, just increase base prob in archetype or call multiple times.
                    # Simple approach: if multiplier > 1, we might send extra events.
                    if self.event_rate_multiplier > 1.0:
                        extra_events = int(self.event_rate_multiplier) - 1
                        for _ in range(extra_events + 1):
                            self.send_event(event)
                    else:
                        if random.random() < self.event_rate_multiplier:
                            self.send_event(event)
            
            # Control simulation speed
            await asyncio.sleep(0.1)
            
        logger.info("Event generation stopped.")

    def send_event(self, event: dict):
        try:
            self.producer.send(self.topic, value=event)
            # logger.debug(f"Sent event: {event['event_id']} for user {event['user_id']}")
        except Exception as e:
            logger.error(f"Failed to send event to Kafka: {e}")

    def stop(self):
        self.is_running = False
        self.producer.flush()
        self.producer.close()

    def set_scenario_params(self, archetype_override: UserArchetype = None, multiplier: float = 1.0):
        self.event_rate_multiplier = multiplier
        if archetype_override:
            logger.info(f"Overriding all users to archetype: {archetype_override}")
            for user in self.users:
                user.archetype = archetype_override
