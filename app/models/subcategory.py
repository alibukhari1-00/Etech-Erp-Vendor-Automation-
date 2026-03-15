from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class SubCategory(Base):
    __tablename__ = "sub_categories"

    id = Column(Integer, primary_key=True, index=True)

    cat_id = Column(Integer, ForeignKey("categories.id"))
    name = Column(String, nullable=False)

    category = relationship("Category", back_populates="sub_categories")
    items = relationship("Item", back_populates="sub_category")