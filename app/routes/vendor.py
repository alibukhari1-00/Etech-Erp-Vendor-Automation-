from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.vendor import VendorCreate, VendorResponse
from app.crud import vendor as vendor_crud

router = APIRouter(prefix="/vendors", tags=["Vendors"])


@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
def create_vendor(data: VendorCreate, db: Session = Depends(get_db)):
    if not data.name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Vendor name is required."
        )
    if data.mobile:
        existing = vendor_crud.get_vendor_by_mobile(db, data.mobile)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A vendor with mobile '{data.mobile}' already exists."
            )
    if data.email:
        existing = vendor_crud.get_vendor_by_email(db, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A vendor with email '{data.email}' already exists."
            )
    if data.loc_id and not vendor_crud.get_location(db, data.loc_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id {data.loc_id} does not exist."
        )
    return vendor_crud.create_vendor(db, data)


@router.get("/", response_model=list[VendorResponse])
def read_vendors(db: Session = Depends(get_db)):
    vendors = vendor_crud.get_vendors(db)
    if not vendors:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vendors found."
        )
    return vendors


@router.get("/{vendor_id}", response_model=VendorResponse)
def read_vendor(vendor_id: int, db: Session = Depends(get_db)):
    if vendor_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="vendor_id must be a positive integer."
        )
    vendor = vendor_crud.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with id {vendor_id} not found."
        )
    return vendor


@router.put("/{vendor_id}", response_model=VendorResponse)
def update_vendor(vendor_id: int, data: VendorCreate, db: Session = Depends(get_db)):
    if vendor_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="vendor_id must be a positive integer."
        )
    vendor = vendor_crud.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with id {vendor_id} not found."
        )
    if data.mobile:
        duplicate = vendor_crud.get_vendor_by_mobile(db, data.mobile)
        if duplicate and duplicate.id != vendor_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Another vendor with mobile '{data.mobile}' already exists."
            )
    if data.email:
        duplicate = vendor_crud.get_vendor_by_email(db, data.email)
        if duplicate and duplicate.id != vendor_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Another vendor with email '{data.email}' already exists."
            )
    if data.loc_id and not vendor_crud.get_location(db, data.loc_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Location with id {data.loc_id} does not exist."
        )
    return vendor_crud.update_vendor(db, vendor_id, data)


@router.delete("/{vendor_id}", status_code=status.HTTP_200_OK)
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    if vendor_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="vendor_id must be a positive integer."
        )
    vendor = vendor_crud.get_vendor(db, vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with id {vendor_id} not found."
        )
    vendor_crud.delete_vendor(db, vendor_id)
    return {"message": f"Vendor '{vendor.name}' deleted successfully."}