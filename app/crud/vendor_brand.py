from sqlalchemy.orm import Session
from app.models.vendor_brand import VendorBrand
from app.schemas.vendor_brand import VendorBrandCreate


def create_vendor_brand(db: Session, data: VendorBrandCreate):
    db_data = VendorBrand(**data.model_dump())
    db.add(db_data)
    db.commit()
    db.refresh(db_data)
    return db_data


def get_vendor_brands(db: Session):
    return db.query(VendorBrand).all()


def get_vendor_brand(db: Session, record_id: int):
    return db.query(VendorBrand).filter(VendorBrand.id == record_id).first()


def get_vendor_brand_by_pair(db: Session, brand_id: int, vendor_id: int):
    return db.query(VendorBrand).filter(
        VendorBrand.brand_id == brand_id,
        VendorBrand.vendor_id == vendor_id
    ).first()


def get_brand(db: Session, brand_id: int):
    from app.models.brand import Brand
    return db.query(Brand).filter(Brand.id == brand_id).first()


def get_vendor(db: Session, vendor_id: int):
    from app.models.vendor import Vendor
    return db.query(Vendor).filter(Vendor.id == vendor_id).first()


def delete_vendor_brand(db: Session, record_id: int):
    record = db.query(VendorBrand).filter(VendorBrand.id == record_id).first()
    db.delete(record)
    db.commit()