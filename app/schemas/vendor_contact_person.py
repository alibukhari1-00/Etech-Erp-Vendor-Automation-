from pydantic import BaseModel, field_validator
from typing import Optional
import re


class VendorContactPersonBase(BaseModel):
    vendor_id: int
    name: str
    mobile: str
    designation: str

    @field_validator("vendor_id")
    @classmethod
    def validate_vendor_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("vendor_id must be a positive integer.")
        return v

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Name cannot be empty or whitespace.")
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters.")
        if len(v) > 100:
            raise ValueError("Name cannot exceed 100 characters.")
        if not re.match(r"^[a-zA-Z\s\'\-\.]+$", v):
            raise ValueError("Name can only contain letters, spaces, hyphens, apostrophes, and dots.")
        return v

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Mobile number cannot be empty.")
        # strip spaces, dashes, parentheses for digit counting
        digits_only = re.sub(r"[\s\-\(\)\+]", "", v)
        if not digits_only.isdigit():
            raise ValueError("Mobile number can only contain digits, spaces, dashes, parentheses, and a leading +.")
        if len(digits_only) < 7:
            raise ValueError("Mobile number must have at least 7 digits.")
        if len(digits_only) > 15:
            raise ValueError("Mobile number cannot exceed 15 digits (E.164 standard).")
        return v

    @field_validator("designation")
    @classmethod
    def validate_designation(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Designation cannot be empty or whitespace.")
        if len(v) < 2:
            raise ValueError("Designation must be at least 2 characters.")
        if len(v) > 100:
            raise ValueError("Designation cannot exceed 100 characters.")
        if not re.match(r"^[a-zA-Z0-9 \s\'\-\.&\/]+$", v):
            raise ValueError("Designation contains invalid characters.")
        return v


class VendorContactPersonCreate(VendorContactPersonBase):
    pass


class VendorContactPersonResponse(VendorContactPersonBase):
    id: int

    class Config:
        from_attributes = True