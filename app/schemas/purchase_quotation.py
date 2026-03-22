from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class PurchaseQuotationBase(BaseModel):
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    lead_time_days: Optional[int] = None
    remarks: Optional[str] = None
    status: str = "pending"

class PurchaseQuotationCreate(PurchaseQuotationBase):
    purchase_demand_id: int
    purchase_demand_item_id: int
    vendor_id: int

class PurchaseQuotationUpdate(PurchaseQuotationBase):
    pass

class PurchaseQuotationResponse(PurchaseQuotationBase):
    id: int
    purchase_demand_id: int
    purchase_demand_item_id: int
    vendor_id: int
    created_at: datetime
    updated_at: datetime
    
    vendor_name: Optional[str] = None

    class Config:
        from_attributes = True

class QuotationRequest(BaseModel):
    vendor_ids: List[int]
    demand_id: int
