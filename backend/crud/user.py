from sqlalchemy.orm import Session
from backend.models.user import User
from backend.schemas.user import UserCreate
from backend.core.security import hash_password


def get_user(db: Session, user_id: int):
    """Получает пользователя по ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    """Получает пользователя по email."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    """Получает пользователя по имени пользователя."""
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: UserCreate):
    """Создает нового пользователя."""
    hashed_password = hash_password(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        password=hashed_password,
        role='reader',
        is_active=True,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
