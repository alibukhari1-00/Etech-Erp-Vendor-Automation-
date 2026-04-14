from sqlalchemy import Column, Integer, Float, ForeignKey, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class PurchaseQuotation(Base):
    __tablename__ = "purchase_quotations"

    id = Column(Integer, primary_key=True, index=True)
    purchase_demand_id = Column(Integer, ForeignKey("purchase_demands.id"), nullable=False)
    purchase_demand_item_id = Column(Integer, ForeignKey("purchase_demand_items.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    unit_price = Column(Float, nullable=True)
    total_price = Column(Float, nullable=True)
    lead_time_days = Column(Integer, nullable=True)
    remarks = Column(Text, nullable=True)
    
    # Status: pending, submitted, selected, rejected
    status = Column(String, default="pending")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    demand = relationship("PurchaseDemand")
    demand_item = relationship("PurchaseDemandItem")
    vendor = relationship("Vendor")
