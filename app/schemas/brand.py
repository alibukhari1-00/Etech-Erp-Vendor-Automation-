from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
import re


VALID_STATUSES = {"active", "inactive", "pending"}


class BrandBase(BaseModel):
    name: str
    company: Optional[str] = None
    loc_id: Optional[int] = None
    status: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Brand name cannot be empty or whitespace.")
        if len(v) < 2:
            raise ValueError("Brand name must be at least 2 characters.")
        if len(v) > 100:
            raise ValueError("Brand name cannot exceed 100 characters.")
        if not re.match(r"^[a-zA-Z0-9 _\-\.&]+$", v):
            raise ValueError("Brand name contains invalid characters.")
        return v

    @field_validator("company")
    @classmethod
    def validate_company(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Company name cannot be empty or whitespace.")
        if len(v) > 150:
            raise ValueError("Company name cannot exceed 150 characters.")
        if not re.match(r"^[a-zA-Z0-9 _\-\.&,]+$", v):
            raise ValueError("Company name contains invalid characters.")
        return v

    @field_validator("loc_id")
    @classmethod
    def validate_loc_id(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if v <= 0:
            raise ValueError("loc_id must be a positive integer.")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if v not in VALID_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(VALID_STATUSES)}.")
        return v


class BrandCreate(BrandBase):
    pass


class BrandResponse(BrandBase):
    id: int

    class Config:
        from_attributes = True