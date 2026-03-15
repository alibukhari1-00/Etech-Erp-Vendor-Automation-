from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.vendor_group import VendorGroupCreate, VendorGroupResponse
from app.crud import vendor_group as crud

router = APIRouter(prefix="/vendor-groups", tags=["Vendor Groups"])


@router.post("/", response_model=VendorGroupResponse, status_code=status.HTTP_201_CREATED)
def create_vendor_group(data: VendorGroupCreate, db: Session = Depends(get_db)):
    if not crud.get_category(db, data.cat_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {data.cat_id} does not exist."
        )
    if not crud.get_vendor(db, data.vendor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with id {data.vendor_id} does not exist."
        )
    existing = crud.get_vendor_group_by_pair(db, data.cat_id, data.vendor_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Vendor {data.vendor_id} is already linked to category {data.cat_id}."
        )
    return crud.create_vendor_group(db, data)


@router.get("/", response_model=list[VendorGroupResponse])
def get_vendor_groups(db: Session = Depends(get_db)):
    groups = crud.get_vendor_groups(db)
    if not groups:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vendor groups found."
        )
    return groups


@router.delete("/{group_id}", status_code=status.HTTP_200_OK)
def delete_vendor_group(group_id: int, db: Session = Depends(get_db)):
    if group_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="group_id must be a positive integer."
        )
    group = crud.get_vendor_group(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor group with id {group_id} not found."
        )
    crud.delete_vendor_group(db, group_id)
    return {"message": f"Vendor {group.vendor_id} unlinked from category {group.cat_id} successfully."}