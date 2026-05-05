from sqlalchemy.orm import Session
from datetime import datetime, timezone

from typing import Optional
from pydantic import BaseModel

from app.models.user import User
from app.core.security import hash_password, create_access_token, verify_password
from app.services.analytics_service import AnalyticsService

class UserSession(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str

import time
from typing import Dict

# Simple in-memory rate limiter: {email: [timestamp, count]}
_login_attempts: Dict[str, list] = {}

class IdentityOrchestrator:
    @staticmethod
    def authenticate(db: Session, email: str, password: str) -> Optional[User]:
        """
        Deep interface for email authentication with built-in rate limiting.
        """
        # 1. Rate Limiting Check
        now = time.time()
        attempt = _login_attempts.get(email, [0, 0])
        if now - attempt[0] < 60: # 1 minute window
            if attempt[1] >= 5: # Max 5 attempts per minute
                return None
            attempt[1] += 1
        else:
            attempt = [now, 1]
        _login_attempts[email] = attempt

        # 2. Authentication Logic
        user = db.query(User).filter(User.email == email).first()
        if user and verify_password(password, user.password_hash):
            _login_attempts.pop(email, None) # Clear on success
            return user
        return None

    @staticmethod
    def authenticate_email(db: Session, email: str, password: str) -> Optional[UserSession]:
        """
        Deep interface for email-based authentication.
        Hides logic for password verification, token generation, and analytics.
        """
        user = IdentityOrchestrator.authenticate(db, email, password)
        if not user:
            return None

        return IdentityOrchestrator._create_session(db, user)

    @staticmethod
    def register_email(db: Session, email: str, password: str) -> User:
        """
        Handles user registration for the email provider.
        """
        new_user = User(
            email=email,
            password_hash=hash_password(password)
        )
        db.add(new_user)
        db.commit()
        return new_user

    @staticmethod
    def _create_session(db: Session, user: User) -> UserSession:
        """
        Common session creation logic shared across all identity providers.
        """
        access_token = create_access_token(data={"sub": str(user.id)})
        
        # Update active state
        user.last_active_hour = datetime.now(timezone.utc).hour

        db.commit()
        
        # Analytics Seam
        AnalyticsService.log_event(db, user.id, "app_open")
        
        return UserSession(
            access_token=access_token,
            user_id=str(user.id),
            email=user.email
        )

    @staticmethod
    def authenticate_social(db: Session, provider: str, token: str) -> Optional[UserSession]:
        """
        Deep interface for social authentication (Google/Apple).
        """
        if provider == "apple":
            identity = IdentityOrchestrator._verify_apple_token(token)
        else:
            return None

        if not identity:
            return None

        # Find or create user
        user = db.query(User).filter(
            User.social_id == identity["sub"],
            User.provider == provider
        ).first()

        if not user:
            user = IdentityOrchestrator._create_social_user(db, identity, provider)

        return IdentityOrchestrator._create_session(db, user)

    @staticmethod
    def _create_social_user(db: Session, identity: dict, provider: str) -> User:
        """
        Private helper to handle social user creation.
        """
        user = User(
            email=identity.get("email"),
            social_id=identity["sub"],
            provider=provider
        )
        db.add(user)
        db.commit()
        return user

    @staticmethod
    def _verify_apple_token(token: str) -> Optional[dict]:
        """
        Private helper to verify Apple ID token.
        In production, this would use 'python-jose' to verify the JWT from Apple.
        """
        # This will be mocked in tests
        pass
