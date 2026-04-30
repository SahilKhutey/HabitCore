import razorpay
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.deps import get_db, auth_required
from app.models.user import User
import os

router = APIRouter()

# Use env variables in production
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "rzp_test_placeholder")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "secret_placeholder")

client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@router.post("/create-order")
def create_order(user=Depends(auth_required)):
    # ₹999.00 subscription
    order_data = {
        "amount": 99900,
        "currency": "INR",
        "payment_capture": 1
    }
    order = client.order.create(data=order_data)
    return order

@router.post("/verify-payment")
def verify_payment(data: dict, user=Depends(auth_required), db: Session = Depends(get_db)):
    try:
        # data contains razorpay_order_id, razorpay_payment_id, razorpay_signature
        client.utility.verify_payment_signature(data)
        
        # Update user to premium
        target_user = db.query(User).filter(User.id == user.id).first()
        target_user.is_premium = True
        db.commit()

        return {"status": "success", "message": "Premium unlocked!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail="Payment verification failed")
