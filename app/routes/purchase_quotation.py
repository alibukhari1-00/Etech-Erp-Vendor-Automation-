from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.dependencies import get_db, get_admin_user
from app.schemas.purchase_quotation import PurchaseQuotationResponse, PurchaseQuotationUpdate
from app.crud import purchase_quotation as pq_crud
from app.models.vendor import Vendor

router = APIRouter(prefix="/purchase-quotations", tags=["Purchase Quotations"])

@router.post("/initiate/{demand_id}", status_code=status.HTTP_201_CREATED)
def initiate_quotations(demand_id: int, db: Session = Depends(get_db)):
    """Creates pending quotation entries for all assigned vendors."""
    count = pq_crud.create_quotation_requests_from_assignments(db, demand_id)
    return {"message": f"Initiated {count} quotation requests."}

@router.get("/demand/{demand_id}", response_model=List[PurchaseQuotationResponse])
def get_demand_quotations(demand_id: int, db: Session = Depends(get_db)):
    quotes = pq_crud.get_quotations_for_demand(db, demand_id)
    
    # Enrichment: Add vendor names
    for q in quotes:
        vendor = db.query(Vendor).filter(Vendor.id == q.vendor_id).first()
        q.vendor_name = vendor.name if vendor else "Unknown Vendor"
        
    return quotes

@router.patch("/{id}", response_model=PurchaseQuotationResponse)
def update_quote_data(id: int, obj_in: PurchaseQuotationUpdate, db: Session = Depends(get_db)):
    quote = pq_crud.update_quotation(db, id, obj_in)
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
        
    vendor = db.query(Vendor).filter(Vendor.id == quote.vendor_id).first()
    quote.vendor_name = vendor.name if vendor else "Unknown Vendor"
    return quote

@router.post("/{id}/select", response_model=PurchaseQuotationResponse)
def select_winner(id: int, db: Session = Depends(get_db)):
    quote = pq_crud.select_quotation(db, id)
    if not quote:
        raise HTTPException(status_code=404, detail="Quotation not found")
        
    vendor = db.query(Vendor).filter(Vendor.id == quote.vendor_id).first()
    quote.vendor_name = vendor.name if vendor else "Unknown Vendor"
    return quote
