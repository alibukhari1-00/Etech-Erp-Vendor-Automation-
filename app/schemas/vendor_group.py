from pydantic import BaseModel, field_validator, model_validator


class VendorGroupBase(BaseModel):
    cat_id: int
    vendor_id: int

    @field_validator("cat_id")
    @classmethod
    def validate_cat_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("cat_id must be a positive integer.")
        return v

    @field_validator("vendor_id")
    @classmethod
    def validate_vendor_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("vendor_id must be a positive integer.")
        return v



class VendorGroupCreate(VendorGroupBase):
    pass


class VendorGroupResponse(VendorGroupBase):
    id: int

    class Config:
        from_attributes = True