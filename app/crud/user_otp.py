from sqlalchemy.orm import Session
from app.models.user_otp import UserOTP
import random
import string
import datetime

def create_otp(db: Session, email: str) -> UserOTP:
    # Delete any existing OTP for this email
    db.query(UserOTP).filter(UserOTP.email == email).delete()
    
    otp_code = "".join(random.choices(string.digits, k=6))
    expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=10)
    
    db_otp = UserOTP(
        email=email,
        otp=otp_code,
        expires_at=expires_at
    )
    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)
    return db_otp

def get_otp(db: Session, email: str, otp: str) -> UserOTP:
    return db.query(UserOTP).filter(
        UserOTP.email == email,
        UserOTP.otp == otp
    ).first()

def delete_otp(db: Session, email: str):
    db.query(UserOTP).filter(UserOTP.email == email).delete()
    db.commit()
