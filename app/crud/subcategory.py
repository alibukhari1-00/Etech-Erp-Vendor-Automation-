from sqlalchemy.orm import Session
from app.models.subcategory import SubCategory
from app.schemas.subcategory import SubCategoryCreate


def create_subcategory(db: Session, subcategory: SubCategoryCreate):
    db_sub = SubCategory(**subcategory.model_dump())
    db.add(db_sub)
    db.commit()
    db.refresh(db_sub)
    return db_sub


def get_subcategories(db: Session):
    return db.query(SubCategory).all()


def get_subcategory(db: Session, sub_id: int):
    return db.query(SubCategory).filter(SubCategory.id == sub_id).first()


def get_subcategory_by_name(db: Session, name: str, cat_id: int):
    return db.query(SubCategory).filter(
        SubCategory.name == name,
        SubCategory.cat_id == cat_id
    ).first()


def get_category(db: Session, cat_id: int):
    from app.models.category import Category
    return db.query(Category).filter(Category.id == cat_id).first()


def update_subcategory(db: Session, sub_id: int, data: SubCategoryCreate):
    sub = db.query(SubCategory).filter(SubCategory.id == sub_id).first()
    for key, value in data.model_dump().items():
        setattr(sub, key, value)
    db.commit()
    db.refresh(sub)
    return sub


def delete_subcategory(db: Session, sub_id: int):
    sub = db.query(SubCategory).filter(SubCategory.id == sub_id).first()
    db.delete(sub)
    db.commit()