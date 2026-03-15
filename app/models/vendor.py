from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base


class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String)
    mobile = Column(String)
    email = Column(String)
    website = Column(String)
    address = Column(String)

    type = Column(Enum(
        "Importer",
        "Trader",
        "WholeSeller",
        "EPC",
        "Installer",
        "Shopkeeper",
        "Manufacturer",
        name="vendor_type"
    ))

    source = Column(Enum(
        "Whatsapp",
        "Email",
        "Call",
        "Portal",
        "Personal",
        "SocialMedia",
        name="vendor_source"
    ))

    whatsapp_group = Column(String)

    loc_id = Column(Integer, ForeignKey("locations.id"))

    location = relationship("Location", back_populates="vendors")

    contacts = relationship("VendorContactPerson", back_populates="vendor")
    vendor_brands = relationship("VendorBrand", back_populates="vendor")
    vendor_groups = relationship("VendorGroup", back_populates="vendor")