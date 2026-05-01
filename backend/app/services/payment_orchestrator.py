import stripe
import os
from app.models.user import User
from sqlalchemy.orm import Session

# Stripe API Key should be in env
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_mock")

class PaymentOrchestrator:
    @staticmethod
    def create_intent(user: User, plan_id: str) -> dict:
        """
        Deep interface to create a Stripe PaymentIntent.
        Hides complexity of calculating amounts and metadata.
        """
        from app.core.constants import PLANS
        
        plan = PLANS.get(plan_id, PLANS["premium_monthly"])
        amount = plan["amount"]
        currency = plan.get("currency", "usd")
        
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            metadata={
                "user_id": str(user.id),
                "plan_id": plan_id
            }
        )

        
        return {
            "client_secret": intent.client_secret,
            "amount": amount
        }

    @staticmethod
    def handle_webhook(db: Session, payload: str, sig_header: str) -> bool:
        """
        Deep interface for handling Stripe webhooks.
        """
        endpoint_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except Exception:
            return False

        if event["type"] == "payment_intent.succeeded":
            intent = event["data"]["object"]
            user_id = intent["metadata"].get("user_id")
            if user_id:
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    user.is_premium = True
                    db.commit()
                    return True
        
        return False
