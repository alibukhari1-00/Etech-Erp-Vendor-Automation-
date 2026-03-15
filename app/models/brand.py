from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class Brand(Base):
    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    company = Column(String, unique=True, index=True)

    loc_id = Column(Integer, ForeignKey("locations.id"))
    status = Column(String)

    location = relationship("Location", back_populates="brands")
    items = relationship("Item", back_populates="brand")