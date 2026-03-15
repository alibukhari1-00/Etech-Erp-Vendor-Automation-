from sqlalchemy.orm import Session
from app.models.vendor_group import VendorGroup
from app.schemas.vendor_group import VendorGroupCreate


def create_vendor_group(db: Session, group: VendorGroupCreate):
    db_group = VendorGroup(**group.model_dump())
    db.add(db_group)
    db.commit()
    db.refresh(db_group)
    return db_group


def get_vendor_groups(db: Session):
    return db.query(VendorGroup).all()


def get_vendor_group(db: Session, group_id: int):
    return db.query(VendorGroup).filter(VendorGroup.id == group_id).first()


def get_vendor_group_by_pair(db: Session, cat_id: int, vendor_id: int):
    return db.query(VendorGroup).filter(
        VendorGroup.cat_id == cat_id,
        VendorGroup.vendor_id == vendor_id
    ).first()


def get_category(db: Session, cat_id: int):
    from app.models.category import Category
    return db.query(Category).filter(Category.id == cat_id).first()


def get_vendor(db: Session, vendor_id: int):
    from app.models.vendor import Vendor
    return db.query(Vendor).filter(Vendor.id == vendor_id).first()


def delete_vendor_group(db: Session, group_id: int):
    group = db.query(VendorGroup).filter(VendorGroup.id == group_id).first()
    db.delete(group)
    db.commit()