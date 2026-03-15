from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)

    scat_id = Column(Integer, ForeignKey("sub_categories.id"))
    brand_id = Column(Integer, ForeignKey("brands.id"))

    power_rating_kv = Column(Float)
    voltage = Column(Float)
    ip_rating = Column(String)
    uom = Column(String)

    purchase_rate = Column(Float)
    profit_percentage = Column(Float)
    sale_rate = Column(Float)
    sale_rate_manual = Column(Float)

    image = Column(String)

    sub_category = relationship("SubCategory", back_populates="items")
    brand = relationship("Brand", back_populates="items")