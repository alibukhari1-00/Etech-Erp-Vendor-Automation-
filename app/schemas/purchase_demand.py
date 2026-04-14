from pydantic import BaseModel, field_validator, Field
from typing import Optional, List
from datetime import datetime

DEMAND_STATUSES = {"draft", "pending_approval", "approved", "rejected", "cancelled"}
EDITABLE_STATUSES = {"draft", "pending_approval"}


# ── Nested: vendor suggestion ─────────────────────────────────────────────────

class VendorSuggestion(BaseModel):
    id: int
    name: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    vendor_type: Optional[str] = None

    class Config:
        from_attributes = True


class VendorLookupResponse(BaseModel):
    vendor_id: int
    vendor_name: Optional[str] = None
    vendor_type: Optional[str] = None
    vendor_group: List[str] = Field(default_factory=list)
    contact_person: Optional[str] = None
    contact_designation: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    brands_supplied: List[str] = Field(default_factory=list)
class VendorLookupResponse(BaseModel):
    vendor_id: int
    vendor_name: Optional[str] = None
    vendor_type: Optional[str] = None
    vendor_group: List[str] = Field(default_factory=list)
    contact_person: Optional[str] = None
    contact_designation: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    brands_supplied: List[str] = Field(default_factory=list)


class QuotationVendorEntry(BaseModel):
    """Vendor enriched with which demand-item IDs they match."""
    vendor_id: int
    vendor_name: Optional[str] = None
    vendor_type: Optional[str] = None
    vendor_group: List[str] = Field(default_factory=list)
    contact_person: Optional[str] = None
    contact_designation: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None
    address: Optional[str] = None
    brands_supplied: List[str] = Field(default_factory=list)
    item_ids: List[int] = Field(default_factory=list)


class PurchaseDemandItemVendorAssign(BaseModel):
    item_id: int
    vendor_ids: List[int]

    @field_validator("vendor_ids")
    @classmethod
    def validate_vendor_ids(cls, v: list[int]) -> list[int]:
        if not v:
            raise ValueError("At least one vendor must be selected for the item.")
        cleaned = list(dict.fromkeys(v))
        if any(vendor_id <= 0 for vendor_id in cleaned):
            raise ValueError("Vendor IDs must be positive integers.")
        return cleaned


class PurchaseDemandVendorAssign(BaseModel):
    assignments: List[PurchaseDemandItemVendorAssign]


class SelectedVendorResponse(BaseModel):
    id: int
    purchase_demand_id: int
    purchase_demand_item_id: Optional[int] = None
    vendor_id: int
    vendor_name: Optional[str] = None

    class Config:
        from_attributes = True


class UserSummary(BaseModel):
    id: int
    full_name: str
    username: str

    class Config:
        from_attributes = True


class ProjectSummary(BaseModel):
    id: int
    project_code: str
    name: str

    class Config:
        from_attributes = True


# ── Nested: item brief ────────────────────────────────────────────────────────

class ItemBrief(BaseModel):
    id: int
    brand_id: Optional[int] = None
    brand_name: Optional[str] = None
    scat_id: Optional[int] = None
    scat_name: Optional[str] = None
    power_rating_kv: Optional[float] = None
    voltage: Optional[float] = None
    ip_rating: Optional[str] = None
    uom: Optional[str] = None
    purchase_rate: Optional[float] = None
    sale_rate: Optional[float] = None

    class Config:
        from_attributes = True


# ── Purchase Demand Items ─────────────────────────────────────────────────────

class PurchaseDemandItemCreate(BaseModel):
    item_id: int
    quantity: float
    notes: Optional[str] = None

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Quantity must be greater than 0.")
        return v


class PurchaseDemandItemResponse(BaseModel):
    id: int
    purchase_demand_id: int
    item_id: int
    quantity: float
    notes: Optional[str] = None
    item: Optional[ItemBrief] = None
    suggested_vendors: List[VendorSuggestion] = Field(default_factory=list)

    class Config:
        from_attributes = True


# ── Purchase Demand ───────────────────────────────────────────────────────────

class PurchaseDemandCreate(BaseModel):
    project_id: int
    remarks: Optional[str] = None
    items: List[PurchaseDemandItemCreate]

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list) -> list:
        if not v:
            raise ValueError("At least one item is required.")
        return v


class PurchaseDemandUpdate(BaseModel):
    remarks: Optional[str] = None
    items: Optional[List[PurchaseDemandItemCreate]] = None

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: Optional[list]) -> Optional[list]:
        if v is not None and len(v) == 0:
            raise ValueError("Items list cannot be empty. Provide at least one item or omit the field.")
        return v


class ApproveRequest(BaseModel):
    remarks: Optional[str] = None


class RejectRequest(BaseModel):
    remarks: str


class PurchaseDemandResponse(BaseModel):
    id: int
    demand_code: str
    project_id: int
    status: str
    remarks: Optional[str] = None
    created_by: int
    updated_by: Optional[int] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    project: Optional[ProjectSummary] = None
    created_by_user: Optional[UserSummary] = None
    approved_by_user: Optional[UserSummary] = None
    selected_vendors: List[SelectedVendorResponse] = Field(default_factory=list)
    items: List[PurchaseDemandItemResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True
