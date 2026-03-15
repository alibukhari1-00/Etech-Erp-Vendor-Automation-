from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.brand import BrandCreate, BrandResponse
from app.crud import brand as crud

router = APIRouter(prefix="/brands", tags=["Brands"])


@router.post("/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
def create_brand(data: BrandCreate, db: Session = Depends(get_db)):
    existing = crud.get_brand_by_name(db, data.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A brand with the name '{data.name}' already exists."
        )
    return crud.create_brand(db, data)


@router.get("/", response_model=list[BrandResponse])
def get_brands(db: Session = Depends(get_db)):
    brands = crud.get_brands(db)
    if not brands:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No brands found."
        )
    return brands


@router.get("/{brand_id}", response_model=BrandResponse)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    if brand_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="brand_id must be a positive integer."
        )
    brand = crud.get_brand(db, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with id {brand_id} not found."
        )
    return brand


@router.put("/{brand_id}", response_model=BrandResponse)
def update_brand(brand_id: int, data: BrandCreate, db: Session = Depends(get_db)):
    if brand_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="brand_id must be a positive integer."
        )
    brand = crud.get_brand(db, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with id {brand_id} not found."
        )
    duplicate = crud.get_brand_by_name(db, data.name)
    if duplicate and duplicate.id != brand_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Another brand with the name '{data.name}' already exists."
        )
    return crud.update_brand(db, brand_id, data)


@router.delete("/{brand_id}", status_code=status.HTTP_200_OK)
def delete_brand(brand_id: int, db: Session = Depends(get_db)):
    if brand_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="brand_id must be a positive integer."
        )
    brand = crud.get_brand(db, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with id {brand_id} not found."
        )
    crud.delete_brand(db, brand_id)
    return {"message": f"Brand '{brand.name}' deleted successfully."}