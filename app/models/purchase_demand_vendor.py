from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db.database import Base


class PurchaseDemandVendor(Base):
    __tablename__ = "purchase_demand_vendors"

    id = Column(Integer, primary_key=True, index=True)
    purchase_demand_id = Column(Integer, ForeignKey("purchase_demands.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "purchase_demand_id",
            "vendor_id",
            name="uq_purchase_demand_vendor",
        ),
    )

    demand = relationship("PurchaseDemand", back_populates="selected_vendors")
    vendor = relationship("Vendor")
