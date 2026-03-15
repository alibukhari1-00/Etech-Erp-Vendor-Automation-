from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.vendor_contact_person import (
    VendorContactPersonCreate,
    VendorContactPersonResponse
)
from app.crud import vendor_contact_person as crud

router = APIRouter(prefix="/vendor-contacts", tags=["Vendor Contacts"])


@router.post("/", response_model=VendorContactPersonResponse, status_code=status.HTTP_201_CREATED)
def create_contact(data: VendorContactPersonCreate, db: Session = Depends(get_db)):
    if not crud.get_vendor(db, data.vendor_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor with id {data.vendor_id} does not exist."
        )
    existing = crud.get_contact_by_mobile(db, data.mobile)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A contact with mobile '{data.mobile}' already exists."
        )
    return crud.create_contact(db, data)


@router.get("/", response_model=list[VendorContactPersonResponse])
def get_contacts(db: Session = Depends(get_db)):
    contacts = crud.get_contacts(db)
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vendor contacts found."
        )
    return contacts


@router.delete("/{contact_id}", status_code=status.HTTP_200_OK)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    if contact_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="contact_id must be a positive integer."
        )
    contact = crud.get_contact(db, contact_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Contact with id {contact_id} not found."
        )
    crud.delete_contact(db, contact_id)
    return {"message": f"Contact '{contact.name}' deleted successfully."}