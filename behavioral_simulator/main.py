import os
import asyncio
import logging
import argparse
from pythonjsonlogger import jsonlogger
from app.generator import EventGenerator
from app.scenarios import ScenarioEngine

def setup_logging():
    logger = logging.getLogger()
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter('%(asctime)s %(levelname)s %(name)s %(message)s')
    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))

async def main():
    setup_logging()
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="HabitCore Behavioral Load Simulator")
    parser.add_argument("--scenario", type=str, default=os.getenv("SCENARIO", "NORMAL"), help="Scenario to run")
    parser.add_argument("--duration", type=int, default=int(os.getenv("DURATION_SEC", "0")), help="Duration in seconds (0 for infinite)")
    parser.add_argument("--users", type=int, default=int(os.getenv("USER_COUNT", "100")), help="Number of synthetic users")
    
    args = parser.parse_args()

    kafka_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    topic = os.getenv("KAFKA_TOPIC", "behavioral_events")

    logger.info(f"Initializing simulator: scenario={args.scenario}, users={args.users}, duration={args.duration}")

    generator = EventGenerator(
        bootstrap_servers=kafka_servers,
        topic=topic,
        user_count=args.users
    )

    engine = ScenarioEngine(generator)

    try:
        await engine.run_scenario(args.scenario, duration_sec=args.duration)
    except KeyboardInterrupt:
        logger.info("Simulation interrupted by user.")
    except Exception as e:
        logger.exception(f"Simulation failed: {e}")
    finally:
        generator.stop()
        logger.info("Simulation cleaned up.")

if __name__ == "__main__":
    asyncio.run(main())
