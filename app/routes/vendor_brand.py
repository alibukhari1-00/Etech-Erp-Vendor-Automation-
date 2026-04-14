from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.vendor_brand import VendorBrandCreate, VendorBrandResponse
from app.crud import vendor_brand as crud

router = APIRouter(prefix="/vendor-brands", tags=["Vendor Brands"])


@router.post("/", response_model=VendorBrandResponse, status_code=status.HTTP_201_CREATED)
def create_vendor_brand(data: VendorBrandCreate, db: Session = Depends(get_db)):
    if not crud.get_brand(db, data.brand_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with id {data.brand_id} does not exist."
        )
    if not crud.get_vendor(db, data.vendor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with id {data.vendor_id} does not exist."
        )
    existing = crud.get_vendor_brand_by_pair(db, data.brand_id, data.vendor_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Vendor {data.vendor_id} is already linked to brand {data.brand_id}."
        )
    return crud.create_vendor_brand(db, data)


@router.get("/", response_model=list[VendorBrandResponse])
def get_vendor_brands(db: Session = Depends(get_db)):
    records = crud.get_vendor_brands(db)
    if not records:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vendor-brand links found."
        )
    return records


@router.delete("/{record_id}", status_code=status.HTTP_200_OK)
def delete_vendor_brand(record_id: int, db: Session = Depends(get_db)):
    if record_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="record_id must be a positive integer."
        )
    record = crud.get_vendor_brand(db, record_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor-brand link with id {record_id} not found."
        )
    crud.delete_vendor_brand(db, record_id)
    return {"message": f"Vendor {record.vendor_id} unlinked from brand {record.brand_id} successfully."}