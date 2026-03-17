from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password


def create_user(db: Session, user: UserCreate):
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password),
        full_name=user.full_name,
        avatar_url=user.avatar_url,
        role=user.role,
        is_active=user.is_active
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session):
    return db.query(User).all()


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


def update_user(db: Session, user_id: int, user_data: UserUpdate):
    user = db.query(User).filter(User.id == user_id).first()
    update_dict = user_data.model_dump(exclude_unset=True)

    if "password" in update_dict and update_dict["password"]:
        update_dict["hashed_password"] = hash_password(update_dict.pop("password"))
    elif "password" in update_dict:
        update_dict.pop("password")

    for key, value in update_dict.items():
        setattr(user, key, value)

    db.commit()
    db.refresh(user)
    return user


def delete_user(db: Session, user_id: int):
    user = db.query(User).filter(User.id == user_id).first()
    db.delete(user)
    db.commit()