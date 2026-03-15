from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class VendorGroup(Base):
    __tablename__ = "vendor_groups"

    id = Column(Integer, primary_key=True, index=True)

    cat_id = Column(Integer, ForeignKey("categories.id"))
    vendor_id = Column(Integer, ForeignKey("vendors.id"))

    category = relationship("Category", back_populates="vendor_groups")
    vendor = relationship("Vendor", back_populates="vendor_groups")