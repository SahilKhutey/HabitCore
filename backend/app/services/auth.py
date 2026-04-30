from sqlalchemy.orm import Session
from app.models.habit import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.user import UserCreate

class AuthService:
    @staticmethod
    def register_user(db: Session, user_in: UserCreate):
        hashed_password = get_password_hash(user_in.password)
        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
