from pydantic import BaseModel, field_validator, model_validator


class VendorBrandBase(BaseModel):
    brand_id: int
    vendor_id: int

    @field_validator("brand_id")
    @classmethod
    def validate_brand_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("brand_id must be a positive integer.")
        return v

    @field_validator("vendor_id")
    @classmethod
    def validate_vendor_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("vendor_id must be a positive integer.")
        return v



class VendorBrandCreate(VendorBrandBase):
    pass


class VendorBrandResponse(VendorBrandBase):
    id: int

    class Config:
        from_attributes = True