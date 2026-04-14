from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.location import LocationCreate, LocationResponse
from app.crud import location as crud

router = APIRouter(prefix="/locations", tags=["Locations"])


@router.post("/", response_model=LocationResponse, status_code=status.HTTP_201_CREATED)
def create_location(data: LocationCreate, db: Session = Depends(get_db)):
    existing = crud.get_location_by_name(db, data.loc_name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A location with the name '{data.loc_name}' already exists."
        )
    return crud.create_location(db, data)


@router.get("/", response_model=list[LocationResponse])
def get_locations(db: Session = Depends(get_db)):
    locations = crud.get_locations(db)
    if not locations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No locations found."
        )
    return locations


@router.get("/{location_id}", response_model=LocationResponse)
def get_location(location_id: int, db: Session = Depends(get_db)):
    if location_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="location_id must be a positive integer."
        )
    location = crud.get_location(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id {location_id} not found."
        )
    return location


@router.put("/{location_id}", response_model=LocationResponse)
def update_location(location_id: int, data: LocationCreate, db: Session = Depends(get_db)):
    if location_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="location_id must be a positive integer."
        )
    location = crud.get_location(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id {location_id} not found."
        )
    duplicate = crud.get_location_by_name(db, data.loc_name)
    if duplicate and duplicate.id != location_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Another location with the name '{data.loc_name}' already exists."
        )
    return crud.update_location(db, location_id, data)


@router.delete("/{location_id}", status_code=status.HTTP_200_OK)
def delete_location(location_id: int, db: Session = Depends(get_db)):
    if location_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="location_id must be a positive integer."
        )
    location = crud.get_location(db, location_id)
    if not location:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id {location_id} not found."
        )
    crud.delete_location(db, location_id)
    return {"message": f"Location '{location.loc_name}' deleted successfully."}