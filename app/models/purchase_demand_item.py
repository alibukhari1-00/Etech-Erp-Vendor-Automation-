from sqlalchemy import Column, Integer, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.database import Base


class PurchaseDemandItem(Base):
    __tablename__ = "purchase_demand_items"

    id = Column(Integer, primary_key=True, index=True)
    purchase_demand_id = Column(
        Integer, ForeignKey("purchase_demands.id"), nullable=False
    )
    item_id = Column(Integer, ForeignKey("items.id"), nullable=False)
    quantity = Column(Float, nullable=False)
    notes = Column(Text, nullable=True)

    demand = relationship("PurchaseDemand", back_populates="items")
    item = relationship("Item")
