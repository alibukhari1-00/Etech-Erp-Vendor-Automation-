from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime

PROJECT_STATUSES = {"active", "completed", "closed"}


class ProjectCreate(BaseModel):
    name: str
    location_id: Optional[int] = None
    status: str = "active"

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Project name cannot be empty.")
        if len(v) < 2:
            raise ValueError("Project name must be at least 2 characters.")
        if len(v) > 200:
            raise ValueError("Project name cannot exceed 200 characters.")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        if v not in PROJECT_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(sorted(PROJECT_STATUSES))}")
        return v


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    location_id: Optional[int] = None
    status: Optional[str] = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Project name cannot be empty.")
        if len(v) > 200:
            raise ValueError("Project name cannot exceed 200 characters.")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if v not in PROJECT_STATUSES:
            raise ValueError(f"Status must be one of: {', '.join(sorted(PROJECT_STATUSES))}")
        return v


class ProjectResponse(BaseModel):
    id: int
    project_code: str
    name: str
    location_id: Optional[int] = None
    status: str
    created_by: int
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
