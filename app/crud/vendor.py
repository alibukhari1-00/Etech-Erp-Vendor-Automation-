from sqlalchemy.orm import Session
from app.models.vendor import Vendor
from app.schemas.vendor import VendorCreate


def create_vendor(db: Session, vendor: VendorCreate):
    db_vendor = Vendor(**vendor.model_dump())
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor


def get_vendors(db: Session):
    return db.query(Vendor).all()


def get_vendor(db: Session, vendor_id: int):
    return db.query(Vendor).filter(Vendor.id == vendor_id).first()


def get_vendor_by_mobile(db: Session, mobile: str):
    return db.query(Vendor).filter(Vendor.mobile == mobile).first()


def get_vendor_by_email(db: Session, email: str):
    return db.query(Vendor).filter(Vendor.email == email).first()


def get_location(db: Session, loc_id: int):
    from app.models.location import Location
    return db.query(Location).filter(Location.id == loc_id).first()


def update_vendor(db: Session, vendor_id: int, vendor_data: VendorCreate):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    for key, value in vendor_data.model_dump().items():
        setattr(vendor, key, value)
    db.commit()
    db.refresh(vendor)
    return vendor


def delete_vendor(db: Session, vendor_id: int):
    vendor = db.query(Vendor).filter(Vendor.id == vendor_id).first()
    db.delete(vendor)
    db.commit()