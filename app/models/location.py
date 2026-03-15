from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base


class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    loc_name = Column(String, nullable=False)

    brands = relationship("Brand", back_populates="location")
    vendors = relationship("Vendor", back_populates="location")