from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user, is_purchaser_access_enabled
from app.schemas.auth import (
    LoginRequest, Token, TokenRefresh, 
    ForgotPasswordRequest, VerifyOTPRequest, ResetPasswordRequest
)
from app.schemas.user import ProfileUpdate, UserResponse
from app.crud import user as user_crud
from app.crud import user_otp as user_otp_crud
from app.core.security import verify_password, create_access_token, create_refresh_token, verify_token, hash_password
from app.core.mail import send_otp_email

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=Token)
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, data.email.strip().lower())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated."
        )
    if user.role == "purchaser" and not is_purchaser_access_enabled(db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Purchaser access is not enabled in the current system yet."
        )

    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
def refresh_token(data: TokenRefresh, db: Session = Depends(get_db)):
    payload = verify_token(data.refresh_token, token_type="refresh")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )

    user_id = payload.get("sub")
    user = user_crud.get_user(db, int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated."
        )
    if user.role == "purchaser" and not is_purchaser_access_enabled(db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Purchaser access is not enabled in the current system yet."
        )

    token_data = {"sub": str(user.id), "email": user.email, "role": user.role}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    return Token(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
@router.patch("/me", response_model=UserResponse)
def update_me(
    data: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if data.email:
        duplicate = user_crud.get_user_by_email(db, data.email)
        if duplicate and duplicate.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Another user with email '{data.email}' already exists."
            )

    if data.username:
        duplicate = user_crud.get_user_by_username(db, data.username)
        if duplicate and duplicate.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Another user with username '{data.username}' already exists."
            )

    return user_crud.update_user(db, current_user.id, data)


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    user = user_crud.get_user_by_email(db, data.email.lower())
    if not user:
        # We don't want to reveal if a user exists or not for security
        return {"message": "If your email is registered, you will receive an OTP shortly."}
    
    otp_record = user_otp_crud.create_otp(db, data.email.lower())
    send_otp_email(data.email.lower(), otp_record.otp)
    
    return {"message": "If your email is registered, you will receive an OTP shortly."}


@router.post("/verify-otp")
def verify_otp(data: VerifyOTPRequest, db: Session = Depends(get_db)):
    otp_record = user_otp_crud.get_otp(db, data.email.lower(), data.otp)
    if not otp_record or otp_record.is_expired():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP."
        )
    
    return {"message": "OTP verified successfully."}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    otp_record = user_otp_crud.get_otp(db, data.email.lower(), data.otp)
    if not otp_record or otp_record.is_expired():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP."
        )
    
    user = user_crud.get_user_by_email(db, data.email.lower())
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    # Update password
    new_hashed_password = hash_password(data.new_password)
    user.hashed_password = new_hashed_password
    db.commit()
    
    # Delete OTP after successful reset
    user_otp_crud.delete_otp(db, data.email.lower())
    
    return {"message": "Password reset successfully."}
