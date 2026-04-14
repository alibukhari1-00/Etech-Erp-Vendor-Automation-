from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user
from app.models.vendor import Vendor
from app.models.brand import Brand
from app.models.category import Category
from app.models.subcategory import SubCategory
from app.models.item import Item
from app.models.location import Location
from app.models.user import User
from app.models.vendor_contact_person import VendorContactPerson
from app.models.vendor_group import VendorGroup
from app.models.vendor_brand import VendorBrand

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return {
        "vendors": db.query(Vendor).count(),
        "brands": db.query(Brand).count(),
        "categories": db.query(Category).count(),
        "subcategories": db.query(SubCategory).count(),
        "items": db.query(Item).count(),
        "locations": db.query(Location).count(),
        "users": db.query(User).count(),
        "vendor_contacts": db.query(VendorContactPerson).count(),
        "vendor_groups": db.query(VendorGroup).count(),
        "vendor_brands": db.query(VendorBrand).count(),
    }
