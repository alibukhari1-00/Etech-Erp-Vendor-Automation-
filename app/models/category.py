from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    sub_categories = relationship("SubCategory", back_populates="category")
    vendor_groups = relationship("VendorGroup", back_populates="category")