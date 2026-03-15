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

    @model_validator(mode="after")
    def validate_ids_not_equal(self) -> "VendorGroupBase":
        if self.cat_id == self.vendor_id:
            raise ValueError("cat_id and vendor_id cannot be the same value.")
        return self


class VendorGroupCreate(VendorGroupBase):
    pass


class VendorGroupResponse(VendorGroupBase):
    id: int

    class Config:
        from_attributes = True