# main.py in healing_service/
import os
import subprocess
import logging
from fastapi import FastAPI, Request
import redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("healing-service")

app = FastAPI(title="HabitCore Healing Service")
redis_client = redis.Redis(host=os.environ.get("REDIS_HOST", "localhost"), port=6379, decode_responses=True)

@app.post("/heal")
async def heal(request: Request):
    payload = await request.json()
    alerts = payload.get("alerts", [])
    
    for alert in alerts:
        alert_name = alert.get("labels", {}).get("alertname")
        status = alert.get("status")
        
        logger.info(f"Received alert: {alert_name} [{status}]")
        
        if status == "firing":
            await handle_firing_alert(alert_name, alert)
        elif status == "resolved":
            await handle_resolved_alert(alert_name, alert)
            
    return {"status": "processed"}

async def handle_firing_alert(name: str, alert: dict):
    if name == "ConsumerStalled":
        logger.warning("Consumer stalled. Restarting nlp_service...")
        restart_container("nlp_service")
        
    elif name == "HighKafkaLag":
        logger.warning("High Kafka Lag detected. Scaling nlp_service...")
        scale_service("nlp_service", 2)
        
    elif name == "CriticalKafkaLag":
        logger.error("CRITICAL Kafka Lag. Activating Degraded Mode.")
        redis_client.set("system_mode", "degraded")
        
    elif name == "LagGrowingFast":
        logger.warning("Lag growing fast. Enabling throttling.")
        redis_client.set("ingestion_rate_limit", "enabled")

async def handle_resolved_alert(name: str, alert: dict):
    if name == "RecoverySignal" or name == "CriticalKafkaLag":
        logger.info("System recovered. Restoring normal mode.")
        redis_client.set("system_mode", "normal")
        redis_client.delete("ingestion_rate_limit")
    elif name == "LagGrowingFast":
        logger.info("Lag stabilized. Disabling throttling.")
        redis_client.delete("ingestion_rate_limit")

def restart_container(name: str):
    try:
        subprocess.run(["docker", "restart", name], check=True)
    except Exception as e:
        logger.error(f"Failed to restart {name}: {e}")

def scale_service(name: str, replicas: int):
    try:
        subprocess.run(["docker-compose", "up", "-d", "--scale", f"{name}={replicas}"], check=True)
    except Exception as e:
        logger.error(f"Failed to scale {name}: {e}")

@app.get("/health")
def health():
    return {"status": "ok", "mode": redis_client.get("system_mode") or "normal"}
