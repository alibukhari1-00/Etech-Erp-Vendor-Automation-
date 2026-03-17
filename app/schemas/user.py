from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
import re


class UserBase(BaseModel):
    email: str
    username: str
    full_name: str
    avatar_url: Optional[str] = None
    role: str = "admin"
    is_active: bool = True

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("Email cannot be empty.")
        if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid email format.")
        return v

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        v = v.strip().lower()
        if not v:
            raise ValueError("Username cannot be empty.")
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if len(v) > 50:
            raise ValueError("Username cannot exceed 50 characters.")
        if not re.match(r"^[a-zA-Z0-9_@.-]+$", v):
            raise ValueError("Username can only contain letters, numbers, underscores, dots, hyphens, and @.")
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Full name cannot be empty.")
        if len(v) < 2:
            raise ValueError("Full name must be at least 2 characters.")
        if len(v) > 100:
            raise ValueError("Full name cannot exceed 100 characters.")
        return v

    @field_validator("avatar_url")
    @classmethod
    def validate_avatar_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            return None
        if len(v) > 5_000_000:
            raise ValueError("Avatar image is too large.")
        if v.startswith("data:image/"):
            return v
        if re.match(r"^https?://", v, re.IGNORECASE):
            return v
        raise ValueError("Avatar must be an image data URL or a valid http/https URL.")

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        v = v.strip().lower()
        if v not in {"admin", "purchaser"}:
            raise ValueError("Role must be either 'admin' or 'purchaser'.")
        return v


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters.")
        if len(v) > 128:
            raise ValueError("Password cannot exceed 128 characters.")
        return v


class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_optional_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return UserBase.validate_email(v)

    @field_validator("username")
    @classmethod
    def validate_optional_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return UserBase.validate_username(v)

    @field_validator("full_name")
    @classmethod
    def validate_optional_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return UserBase.validate_full_name(v)

    @field_validator("role")
    @classmethod
    def validate_optional_role(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return UserBase.validate_role(v)

    @field_validator("avatar_url")
    @classmethod
    def validate_optional_avatar_url(cls, v: Optional[str]) -> Optional[str]:
        return UserBase.validate_avatar_url(v)

    @field_validator("password")
    @classmethod
    def validate_optional_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        return UserCreate.validate_password(v)


class ProfileUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    password: Optional[str] = None

    @field_validator("email")
    @classmethod
    def validate_optional_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return UserBase.validate_email(v)

    @field_validator("username")
    @classmethod
    def validate_optional_username(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return UserBase.validate_username(v)

    @field_validator("full_name")
    @classmethod
    def validate_optional_full_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        return UserBase.validate_full_name(v)

    @field_validator("avatar_url")
    @classmethod
    def validate_optional_avatar_url(cls, v: Optional[str]) -> Optional[str]:
        return UserBase.validate_avatar_url(v)

    @field_validator("password")
    @classmethod
    def validate_optional_password(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        return UserCreate.validate_password(v)


class UserResponse(UserBase):
    id: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True