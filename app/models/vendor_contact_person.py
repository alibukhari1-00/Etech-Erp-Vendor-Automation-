from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base


class VendorContactPerson(Base):
    __tablename__ = "vendor_contact_persons"

    id = Column(Integer, primary_key=True, index=True)

    vendor_id = Column(Integer, ForeignKey("vendors.id"))

    name = Column(String)
    mobile = Column(String)
    designation = Column(String)

    vendor = relationship("Vendor", back_populates="contacts")