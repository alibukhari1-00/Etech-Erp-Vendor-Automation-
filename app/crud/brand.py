from sqlalchemy.orm import Session
from app.models.brand import Brand
from app.schemas.brand import BrandCreate


def create_brand(db: Session, brand: BrandCreate):
    db_brand = Brand(**brand.model_dump())
    db.add(db_brand)
    db.commit()
    db.refresh(db_brand)
    return db_brand


def get_brands(db: Session):
    return db.query(Brand).all()


def get_brand(db: Session, brand_id: int):
    return db.query(Brand).filter(Brand.id == brand_id).first()


def get_brand_by_name(db: Session, name: str):
    return db.query(Brand).filter(Brand.name == name).first()


def update_brand(db: Session, brand_id: int, brand_data: BrandCreate):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    for key, value in brand_data.model_dump().items():
        setattr(brand, key, value)
    db.commit()
    db.refresh(brand)
    return brand


def delete_brand(db: Session, brand_id: int):
    brand = db.query(Brand).filter(Brand.id == brand_id).first()
    db.delete(brand)
    db.commit()