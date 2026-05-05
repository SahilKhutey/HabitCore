import asyncio
import json
import logging
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.api.deps import get_db, auth_required
from app.services.context_store.manager import ContextManager
import os

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/stream")
async def nudge_stream(
    request: Request,
    user = Depends(auth_required),
    db: Session = Depends(get_db)
):
    """
    SSE stream for real-time behavioral nudges.
    """
    ctx_manager = ContextManager(host=os.environ.get("REDIS_HOST", "localhost"))
    pubsub = ctx_manager.r.pubsub()
    channel = f"nudges:{user.id}"
    pubsub.subscribe(channel)
    
    logger.info(f"User {user.id} subscribed to nudge stream via channel {channel}")

    async def event_generator():
        try:
            while True:
                # Check for client disconnect
                if await request.is_disconnected():
                    logger.info(f"User {user.id} disconnected from nudge stream")
                    break
                
                # Check for messages (non-blocking)
                message = pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    data = message['data']
                    yield f"data: {data}\n\n"
                
                await asyncio.sleep(0.5) # Poll Redis pubsub lightly
        except Exception as e:
            logger.error(f"Error in nudge stream for user {user.id}: {e}")
        finally:
            pubsub.unsubscribe(channel)
            pubsub.close()

    return StreamingResponse(event_generator(), media_type="text/event-stream")
