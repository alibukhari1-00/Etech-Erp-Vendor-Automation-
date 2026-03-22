from sqlalchemy.orm import Session
from app.models.purchase_quotation import PurchaseQuotation
from app.models.purchase_demand_vendor import PurchaseDemandVendor
from app.schemas.purchase_quotation import PurchaseQuotationCreate, PurchaseQuotationUpdate

def create_quotation_requests_from_assignments(db: Session, demand_id: int):
    """
    Creates 'pending' quotations for all vendors assigned to items in a demand.
    """
    # Get all assigned vendors for this demand
    assignments = db.query(PurchaseDemandVendor).filter(
        PurchaseDemandVendor.purchase_demand_id == demand_id
    ).all()
    
    created_count = 0
    for assign in assignments:
        # Check if already exists
        exists = db.query(PurchaseQuotation).filter(
            PurchaseQuotation.purchase_demand_id == demand_id,
            PurchaseQuotation.purchase_demand_item_id == assign.purchase_demand_item_id,
            PurchaseQuotation.vendor_id == assign.vendor_id
        ).first()
        
        if not exists:
            db_quote = PurchaseQuotation(
                purchase_demand_id=demand_id,
                purchase_demand_item_id=assign.purchase_demand_item_id,
                vendor_id=assign.vendor_id,
                status="pending"
            )
            db.add(db_quote)
            created_count += 1
            
    db.commit()
    return created_count

def get_quotations_for_demand(db: Session, demand_id: int) -> list[PurchaseQuotation]:
    return db.query(PurchaseQuotation).filter(
        PurchaseQuotation.purchase_demand_id == demand_id
    ).all()

def update_quotation(db: Session, quotation_id: int, obj_in: PurchaseQuotationUpdate) -> PurchaseQuotation:
    db_obj = db.query(PurchaseQuotation).filter(PurchaseQuotation.id == quotation_id).first()
    if not db_obj:
        return None
        
    update_data = obj_in.model_dump(exclude_unset=True)
    for field in update_data:
        setattr(db_obj, field, update_data[field])
        
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def select_quotation(db: Session, quotation_id: int) -> PurchaseQuotation:
    """Selects a quotation and marks others for the SAME item as 'rejected'."""
    db_obj = db.query(PurchaseQuotation).filter(PurchaseQuotation.id == quotation_id).first()
    if not db_obj:
        return None
        
    # Mark others for this item as rejected
    db.query(PurchaseQuotation).filter(
        PurchaseQuotation.purchase_demand_item_id == db_obj.purchase_demand_item_id,
        PurchaseQuotation.id != quotation_id
    ).update({"status": "rejected"})
    
    db_obj.status = "selected"
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
