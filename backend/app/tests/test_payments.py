import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.db.base import Base
from app.models.user import User
from app.services.payment_orchestrator import PaymentOrchestrator

@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()

def test_create_payment_intent(db, mocker):
    # RED: PaymentOrchestrator doesn't exist
    user = User(email="pay@example.com")
    db.add(user)
    db.commit()
    
    # Mock Stripe
    mock_stripe = mocker.patch("stripe.PaymentIntent.create")
    mock_stripe.return_value = mocker.Mock(client_secret="pi_secret_123")
    
    # Act
    result = PaymentOrchestrator.create_intent(user, "premium_yearly")
    
    # Assert
    assert result["client_secret"] == "pi_secret_123"
    assert mock_stripe.called

def test_handle_webhook_success(db, mocker):
    user = User(email="customer@example.com", is_premium=False)
    db.add(user)
    db.commit()
    
    # Mock Stripe Webhook construction
    mock_construct = mocker.patch("stripe.Webhook.construct_event")
    mock_construct.return_value = {
        "type": "payment_intent.succeeded",
        "data": {
            "object": {
                "metadata": {"user_id": str(user.id)}
            }
        }
    }
    
    # Act
    success = PaymentOrchestrator.handle_webhook(db, "payload", "sig")
    
    # Assert
    assert success is True
    db.refresh(user)
    assert user.is_premium is True

