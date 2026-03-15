from sqlalchemy.orm import Session
from app.models.location import Location
from app.schemas.location import LocationCreate


def create_location(db: Session, location: LocationCreate):
    db_location = Location(**location.model_dump())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location


def get_locations(db: Session):
    return db.query(Location).all()


def get_location(db: Session, location_id: int):
    return db.query(Location).filter(Location.id == location_id).first()


def get_location_by_name(db: Session, loc_name: str):
    return db.query(Location).filter(Location.loc_name == loc_name).first()


def update_location(db: Session, location_id: int, location_data: LocationCreate):
    location = db.query(Location).filter(Location.id == location_id).first()
    for key, value in location_data.model_dump().items():
        setattr(location, key, value)
    db.commit()
    db.refresh(location)
    return location


def delete_location(db: Session, location_id: int):
    location = db.query(Location).filter(Location.id == location_id).first()
    db.delete(location)
    db.commit()