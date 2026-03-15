from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
import re


VALID_UOM = {"pcs", "kg", "g", "ltr", "ml", "m", "cm", "mm", "ft", "inch", "box", "pack", "set", "pair"}


class ItemBase(BaseModel):
    scat_id: int
    brand_id: int
    power_rating_kv: Optional[float] = None
    voltage: Optional[float] = None
    ip_rating: Optional[str] = None
    uom: Optional[str] = None
    purchase_rate: Optional[float] = None
    profit_percentage: Optional[float] = None
    sale_rate: Optional[float] = None
    sale_rate_manual: Optional[float] = None
    image: Optional[str] = None

    @field_validator("scat_id")
    @classmethod
    def validate_scat_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("scat_id must be a positive integer.")
        return v

    @field_validator("brand_id")
    @classmethod
    def validate_brand_id(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("brand_id must be a positive integer.")
        return v

    @field_validator("power_rating_kv")
    @classmethod
    def validate_power_rating_kv(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError("power_rating_kv cannot be negative.")
        if v > 100000:
            raise ValueError("power_rating_kv exceeds maximum allowed value (100000 kV).")
        return round(v, 4)

    @field_validator("voltage")
    @classmethod
    def validate_voltage(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError("Voltage cannot be negative.")
        if v > 100000:
            raise ValueError("Voltage exceeds maximum allowed value (100000 V).")
        return round(v, 4)

    @field_validator("ip_rating")
    @classmethod
    def validate_ip_rating(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().upper()
        if not re.match(r"^IP\d{2}$", v):
            raise ValueError("ip_rating must follow the format 'IP' followed by two digits (e.g., IP65).")
        return v

    @field_validator("uom")
    @classmethod
    def validate_uom(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip().lower()
        if v not in VALID_UOM:
            raise ValueError(f"uom must be one of: {', '.join(sorted(VALID_UOM))}.")
        return v

    @field_validator("purchase_rate")
    @classmethod
    def validate_purchase_rate(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError("purchase_rate cannot be negative.")
        if v > 99_999_999:
            raise ValueError("purchase_rate exceeds maximum allowed value.")
        return round(v, 2)

    @field_validator("profit_percentage")
    @classmethod
    def validate_profit_percentage(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError("profit_percentage cannot be negative.")
        if v > 10000:
            raise ValueError("profit_percentage cannot exceed 10000%.")
        return round(v, 4)

    @field_validator("sale_rate")
    @classmethod
    def validate_sale_rate(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError("sale_rate cannot be negative.")
        if v > 99_999_999:
            raise ValueError("sale_rate exceeds maximum allowed value.")
        return round(v, 2)

    @field_validator("sale_rate_manual")
    @classmethod
    def validate_sale_rate_manual(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return v
        if v < 0:
            raise ValueError("sale_rate_manual cannot be negative.")
        if v > 99_999_999:
            raise ValueError("sale_rate_manual exceeds maximum allowed value.")
        return round(v, 2)

    @field_validator("image")
    @classmethod
    def validate_image(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        v = v.strip()
        if not v:
            raise ValueError("Image path cannot be empty or whitespace.")
        if len(v) > 500:
            raise ValueError("Image path cannot exceed 500 characters.")
        allowed_extensions = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".svg"}
        ext = "." + v.split(".")[-1].lower() if "." in v else ""
        if ext not in allowed_extensions:
            raise ValueError(f"Image must be one of: {', '.join(sorted(allowed_extensions))}.")
        return v

    @model_validator(mode="after")
    def validate_sale_rate_vs_purchase_rate(self) -> "ItemBase":
        if (
            self.sale_rate is not None
            and self.purchase_rate is not None
            and self.sale_rate < self.purchase_rate
        ):
            raise ValueError("sale_rate cannot be less than purchase_rate.")
        if (
            self.sale_rate_manual is not None
            and self.purchase_rate is not None
            and self.sale_rate_manual < self.purchase_rate
        ):
            raise ValueError("sale_rate_manual cannot be less than purchase_rate.")
        return self


class ItemCreate(ItemBase):
    pass


class ItemResponse(ItemBase):
    id: int

    class Config:
        from_attributes = True