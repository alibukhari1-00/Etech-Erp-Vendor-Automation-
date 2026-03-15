from sqlalchemy.orm import Session
from app.models.vendor_contact_person import VendorContactPerson
from app.schemas.vendor_contact_person import VendorContactPersonCreate


def create_contact(db: Session, contact: VendorContactPersonCreate):
    db_contact = VendorContactPerson(**contact.model_dump())
    db.add(db_contact)
    db.commit()
    db.refresh(db_contact)
    return db_contact


def get_contacts(db: Session):
    return db.query(VendorContactPerson).all()


def get_contact(db: Session, contact_id: int):
    return db.query(VendorContactPerson).filter(
        VendorContactPerson.id == contact_id
    ).first()


def get_contact_by_mobile(db: Session, mobile: str):
    return db.query(VendorContactPerson).filter(
        VendorContactPerson.mobile == mobile
    ).first()


def get_vendor(db: Session, vendor_id: int):
    from app.models.vendor import Vendor
    return db.query(Vendor).filter(Vendor.id == vendor_id).first()


def delete_contact(db: Session, contact_id: int):
    contact = db.query(VendorContactPerson).filter(
        VendorContactPerson.id == contact_id
    ).first()
    db.delete(contact)
    db.commit()