from pydantic import BaseModel, field_validator
import re


class SubCategoryBase(BaseModel):
    name: str
    cat_id: int

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Sub-category name cannot be empty or whitespace.")
        if len(v) < 2:
            raise ValueError("Sub-category name must be at least 2 characters.")
        if len(v) > 100:
            raise ValueError("Sub-category name cannot exceed 100 characters.")
        if not re.match(r"^[a-zA-Z0-9 _\-\.&]+$", v):
            raise ValueError("Sub-category name contains invalid characters.")
        return v

    @field_validator("cat_id")
    @classmethod
    def validate_cat_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("cat_id must be a positive integer.")
        return v


class SubCategoryCreate(SubCategoryBase):
    pass


class SubCategoryResponse(SubCategoryBase):
    id: int

    class Config:
        from_attributes = True