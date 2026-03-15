from sqlalchemy.orm import Session
from app.models.item import Item
from app.schemas.item import ItemCreate


def create_item(db: Session, item: ItemCreate):
    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_items(db: Session):
    return db.query(Item).all()


def get_item(db: Session, item_id: int):
    return db.query(Item).filter(Item.id == item_id).first()


def get_brand(db: Session, brand_id: int):
    from app.models.brand import Brand
    return db.query(Brand).filter(Brand.id == brand_id).first()


def get_scat(db: Session, scat_id: int):
    from app.models.subcategory import SubCategory
    return db.query(SubCategory).filter(SubCategory.id == scat_id).first()


def update_item(db: Session, item_id: int, item_data: ItemCreate):
    item = db.query(Item).filter(Item.id == item_id).first()
    for key, value in item_data.model_dump().items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item_id: int):
    item = db.query(Item).filter(Item.id == item_id).first()
    db.delete(item)
    db.commit()