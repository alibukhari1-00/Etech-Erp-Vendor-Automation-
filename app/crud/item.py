from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, cast, String
from app.models.item import Item
from app.schemas.item import ItemCreate


def create_item(db: Session, item: ItemCreate):
    db_item = Item(**item.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_items(db: Session):
    return db.query(Item).options(
        joinedload(Item.brand), joinedload(Item.sub_category)
    ).all()


def get_item(db: Session, item_id: int):
    return db.query(Item).options(
        joinedload(Item.brand), joinedload(Item.sub_category)
    ).filter(Item.id == item_id).first()


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


def search_items(db: Session, q: str, limit: int = 50):
    from app.models.brand import Brand
    from app.models.subcategory import SubCategory
    from app.models.category import Category

    query = (q or "").strip().lower()
    if not query:
        return []

    numeric = None
    cleaned = query.replace("kw", "").replace("kv", "").strip()
    try:
        numeric = float(cleaned)
    except ValueError:
        numeric = None

    filters = [
        Brand.name.ilike(f"%{query}%"),
        Category.name.ilike(f"%{query}%"),
        SubCategory.name.ilike(f"%{query}%"),
        cast(Item.power_rating_kv, String).ilike(f"%{query}%"),
        cast(Item.voltage, String).ilike(f"%{query}%"),
        Item.uom.ilike(f"%{query}%"),
        Item.ip_rating.ilike(f"%{query}%"),
    ]
    if numeric is not None:
        filters.append(Item.power_rating_kv == numeric)

    rows = (
        db.query(
            Item.id.label("item_id"),
            Brand.name.label("brand"),
            Category.name.label("category"),
            SubCategory.name.label("sub_category"),
            Item.power_rating_kv,
            Item.voltage,
            Item.uom,
        )
        .join(Brand, Item.brand_id == Brand.id)
        .join(SubCategory, Item.scat_id == SubCategory.id)
        .join(Category, SubCategory.cat_id == Category.id)
        .filter(or_(*filters))
        .order_by(Item.id.desc())
        .limit(limit)
        .all()
    )

    return rows