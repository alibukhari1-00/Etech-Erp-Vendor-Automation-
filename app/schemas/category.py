from pydantic import BaseModel, field_validator
import re


class CategoryBase(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Category name cannot be empty or whitespace.")
        if len(v) < 2:
            raise ValueError("Category name must be at least 2 characters.")
        if len(v) > 100:
            raise ValueError("Category name cannot exceed 100 characters.")
        if not re.match(r"^[a-zA-Z0-9 _\-\.&]+$", v):
            raise ValueError("Category name contains invalid characters.")
        return v


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True