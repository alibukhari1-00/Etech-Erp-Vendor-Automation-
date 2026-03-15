from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class VendorBrand(Base):
    __tablename__ = "vendor_brands"

    id = Column(Integer, primary_key=True, index=True)

    brand_id = Column(Integer, ForeignKey("brands.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))

    brand = relationship("Brand")
    vendor = relationship("Vendor", back_populates="vendor_brands")