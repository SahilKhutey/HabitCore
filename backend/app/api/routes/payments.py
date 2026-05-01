from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.orm import Session
from app.api.deps import get_db, auth_required
from app.services.payment_orchestrator import PaymentOrchestrator

router = APIRouter()

@router.post("/create-intent")
def create_payment_intent(plan_id: str, user=Depends(auth_required), db: Session = Depends(get_db)):
    """
    Creates a payment intent for a specific premium plan.
    """
    try:
        return PaymentOrchestrator.create_intent(user, plan_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), db: Session = Depends(get_db)):
    """
    Stripe webhook endpoint to handle payment successes.
    """
    payload = await request.body()
    if not stripe_signature:
        raise HTTPException(status_code=400, detail="Missing signature")
        
    success = PaymentOrchestrator.handle_webhook(db, payload, stripe_signature)
    if success:
        return {"status": "success"}
    
    # We return 200 even on failure to acknowledge receipt to Stripe, 
    # but we log the error or return a specific message for debugging.
    return {"status": "event_ignored"}
