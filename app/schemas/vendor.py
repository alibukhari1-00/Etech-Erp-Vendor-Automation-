from pydantic import BaseModel, field_validator
from typing import Optional
import re


VALID_TYPES = {"supplier", "manufacturer", "distributor", "retailer", "wholesaler"}
VALID_SOURCES = {"referral", "online", "cold_call", "exhibition", "social_media", "other"}


class VendorBase(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    type: Optional[str] = None
    source: Optional[str] = None
    whatsapp_group: Optional[str] = None
    loc_id: Optional[int] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Vendor name cannot be empty or whitespace.")
        if len(v) < 2:
            raise ValueError("Vendor name must be at least 2 characters.")
        if len(v) > 150:
            raise ValueError("Vendor name cannot exceed 150 characters.")
        if not re.match(r"^[a-zA-Z0-9 _\-\.&,\(\)]+$", v):
            raise ValueError("Vendor name contains invalid characters.")
        return v

    @field_validator("mobile")
    @classmethod
    def validate_mobile(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Mobile number cannot be empty.")
        digits_only = re.sub(r"[\s\-\(\)\+]", "", v)
        if not digits_only.isdigit():
            raise ValueError("Mobile number can only contain digits, spaces, dashes, parentheses, and a leading +.")
        if len(digits_only) < 7:
            raise ValueError("Mobile number must have at least 7 digits.")
        if len(digits_only) > 15:
            raise ValueError("Mobile number cannot exceed 15 digits (E.164 standard).")
        return v

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if not v:
            raise ValueError("Email cannot be empty or whitespace.")
        if len(v) > 254:
            raise ValueError("Email cannot exceed 254 characters.")
        if not re.match(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$", v):
            raise ValueError("Invalid email address format.")
        return v

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Website cannot be empty or whitespace.")
        if len(v) > 255:
            raise ValueError("Website URL cannot exceed 255 characters.")
        if not re.match(r"^(https?:\/\/)?(www\.)?[a-zA-Z0-9\-]+(\.[a-zA-Z]{2,})+([\/\w\-\.?=%&]*)?$", v):
            raise ValueError("Invalid website URL format.")
        return v

    @field_validator("address")
    @classmethod
    def validate_address(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Address cannot be empty or whitespace.")
        if len(v) < 5:
            raise ValueError("Address must be at least 5 characters.")
        if len(v) > 300:
            raise ValueError("Address cannot exceed 300 characters.")
        return v

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if v not in VALID_TYPES:
            raise ValueError(f"Type must be one of: {', '.join(sorted(VALID_TYPES))}.")
        return v

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if v not in VALID_SOURCES:
            raise ValueError(f"Source must be one of: {', '.join(sorted(VALID_SOURCES))}.")
        return v

    @field_validator("whatsapp_group")
    @classmethod
    def validate_whatsapp_group(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("WhatsApp group name cannot be empty or whitespace.")
        if len(v) > 100:
            raise ValueError("WhatsApp group name cannot exceed 100 characters.")
        if not re.match(r"^[a-zA-Z0-9 _\-\.&]+$", v):
            raise ValueError("WhatsApp group name contains invalid characters.")
        return v

    @field_validator("loc_id")
    @classmethod
    def validate_loc_id(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return v
        if v <= 0:
            raise ValueError("loc_id must be a positive integer.")
        return v


class VendorCreate(VendorBase):
    pass


class VendorResponse(VendorBase):
    id: int

    class Config:
        from_attributes = True