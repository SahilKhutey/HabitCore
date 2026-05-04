import logging
import asyncio
from typing import Dict, Any
from .archetypes import UserArchetype
from .generator import EventGenerator

logger = logging.getLogger(__name__)

class ScenarioEngine:
    def __init__(self, generator: EventGenerator):
        self.generator = generator

    async def run_scenario(self, scenario_name: str, duration_sec: int = 60):
        logger.info(f"Executing scenario: {scenario_name}")
        
        if scenario_name == "NORMAL":
            await self.generator.run(duration_sec=duration_sec)
            
        elif scenario_name == "TRAFFIC_SPIKE":
            # 5x traffic increase
            self.generator.set_scenario_params(multiplier=5.0)
            await self.generator.run(duration_sec=duration_sec)
            
        elif scenario_name == "BINGE_WAVE":
            # All users become binge users
            self.generator.set_scenario_params(archetype_override=UserArchetype.BINGE, multiplier=2.0)
            await self.generator.run(duration_sec=duration_sec)
            
        elif scenario_name == "CRITICAL_RELAPSE_BURST":
            # Simulate many drop-off users at once
            self.generator.set_scenario_params(archetype_override=UserArchetype.DROPOFF, multiplier=3.0)
            await self.generator.run(duration_sec=duration_sec)
            
        elif scenario_name == "NLP_SLOWDOWN":
            # This requires external control of the NLP service, or 
            # the generator can simulate it by sending larger payloads or 
            # we just monitor how the system handles it if we trigger it externally.
            # For now, let's just run high load.
            self.generator.set_scenario_params(multiplier=2.5)
            await self.generator.run(duration_sec=duration_sec)
            
        else:
            logger.error(f"Unknown scenario: {scenario_name}")

    def reset(self):
        self.generator.set_scenario_params(multiplier=1.0)
        # Re-randomize user archetypes
        for user in self.generator.users:
            import random
            user.archetype = random.choice(list(UserArchetype))
