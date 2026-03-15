from pydantic import BaseModel, field_validator
import re


class LocationBase(BaseModel):
    loc_name: str

    @field_validator("loc_name")
    @classmethod
    def validate_loc_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Location name cannot be empty or whitespace.")
        if len(v) < 2:
            raise ValueError("Location name must be at least 2 characters.")
        if len(v) > 100:
            raise ValueError("Location name cannot exceed 100 characters.")
        if not re.match(r"^[a-zA-Z0-9 _\-\.\,\#\/]+$", v):
            raise ValueError("Location name contains invalid characters.")
        return v


class LocationCreate(LocationBase):
    pass


class LocationResponse(LocationBase):
    id: int

    class Config:
        from_attributes = True