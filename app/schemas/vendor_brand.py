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

    @model_validator(mode="after")
    def validate_ids_not_equal(self) -> "VendorBrandBase":
        if self.brand_id == self.vendor_id:
            raise ValueError("brand_id and vendor_id cannot be the same value.")
        return self


class VendorBrandCreate(VendorBrandBase):
    pass


class VendorBrandResponse(VendorBrandBase):
    id: int

    class Config:
        from_attributes = True