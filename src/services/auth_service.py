import bcrypt
from sqlalchemy.orm import Session
from src.database.models import User
from loguru import logger

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def create_user(db: Session, username: str, password: str, name: str = None, is_admin: bool = False):
        try:
            hashed = AuthService.hash_password(password)
            user = User(username=username, password_hash=hashed, name=name, is_admin=is_admin)
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"User created: {username}")
            return user
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to create user: {e}")
            return None

    @staticmethod
    def authenticate(db: Session, username: str, password: str):
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not AuthService.verify_password(password, user.password_hash):
            return None
        return user
