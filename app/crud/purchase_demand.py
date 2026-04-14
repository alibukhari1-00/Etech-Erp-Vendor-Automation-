from datetime import datetime, timezone
from sqlalchemy import inspect
from sqlalchemy.orm import Session, selectinload
from app.models.purchase_demand import PurchaseDemand
from app.models.purchase_demand_item import PurchaseDemandItem
from app.models.purchase_demand_vendor import PurchaseDemandVendor
from app.models.item import Item
from app.models.vendor_brand import VendorBrand
from app.models.vendor import Vendor
from app.models.vendor_contact_person import VendorContactPerson
from app.models.vendor_group import VendorGroup
from app.models.subcategory import SubCategory
from app.schemas.purchase_demand import PurchaseDemandCreate, PurchaseDemandUpdate


# ── Code generation ───────────────────────────────────────────────────────────

def _next_demand_code(db: Session) -> str:
    last = db.query(PurchaseDemand).order_by(PurchaseDemand.id.desc()).first()
    next_num = (last.id + 1) if last else 1
    return f"PD-{next_num:04d}"


def _purchase_demand_vendor_has_demand_column(db: Session) -> bool:
    try:
        columns = {column["name"] for column in inspect(db.bind).get_columns("purchase_demand_vendors")}
        if "purchase_demand_id" in columns:
            return "purchase_demand_id"
        elif "demand_id" in columns:
            return "demand_id"
        else:
            return None
    except Exception:
        return None


def _get_existing_draft_demand(
    db: Session,
    project_id: int,
    created_by: int,
) -> PurchaseDemand | None:
    return (
        db.query(PurchaseDemand)
        .filter(
            PurchaseDemand.project_id == project_id,
            PurchaseDemand.created_by == created_by,
            PurchaseDemand.status == "draft",
        )
        .order_by(PurchaseDemand.id.desc())
        .first()
    )


# ── Create ────────────────────────────────────────────────────────────────────

def create_purchase_demand(
    db: Session, data: PurchaseDemandCreate, created_by: int
) -> PurchaseDemand:
    existing_draft = _get_existing_draft_demand(db, data.project_id, created_by)
    if existing_draft:
        if data.remarks is not None:
            existing_draft.remarks = data.remarks
        existing_draft.updated_by = created_by

        existing_items_by_id = {line.item_id: line for line in existing_draft.items}
        for item_data in data.items:
            existing_line = existing_items_by_id.get(item_data.item_id)
            if existing_line:
                existing_line.quantity = float(existing_line.quantity or 0) + float(item_data.quantity)
                if item_data.notes is not None:
                    existing_line.notes = item_data.notes
            else:
                db.add(
                    PurchaseDemandItem(
                        purchase_demand_id=existing_draft.id,
                        item_id=item_data.item_id,
                        quantity=item_data.quantity,
                        notes=item_data.notes,
                    )
                )

        db.commit()
        db.refresh(existing_draft)
        return existing_draft

    demand = PurchaseDemand(
        demand_code=_next_demand_code(db),
        project_id=data.project_id,
        status="draft",
        remarks=data.remarks,
        created_by=created_by,
    )
    db.add(demand)
    db.flush()  # obtain demand.id before inserting items

    for item_data in data.items:
        db.add(
            PurchaseDemandItem(
                purchase_demand_id=demand.id,
                item_id=item_data.item_id,
                quantity=item_data.quantity,
                notes=item_data.notes,
            )
        )

    db.commit()
    db.refresh(demand)
    return demand


# ── Read ──────────────────────────────────────────────────────────────────────

def get_purchase_demands(
    db: Session, project_id: int | None = None
) -> list[PurchaseDemand]:
    q = db.query(PurchaseDemand).options(
        selectinload(PurchaseDemand.items).selectinload(PurchaseDemandItem.item).selectinload(Item.sub_category),
        selectinload(PurchaseDemand.items).selectinload(PurchaseDemandItem.item).selectinload(Item.brand),
        selectinload(PurchaseDemand.project),
        selectinload(PurchaseDemand.creator),
        selectinload(PurchaseDemand.approver),
    )
    if project_id is not None:
        q = q.filter(PurchaseDemand.project_id == project_id)
    return q.order_by(PurchaseDemand.id.desc()).all()


def get_purchase_demand(db: Session, demand_id: int) -> PurchaseDemand | None:
    return (
        db.query(PurchaseDemand)
        .options(
            selectinload(PurchaseDemand.items).selectinload(PurchaseDemandItem.item).selectinload(Item.sub_category),
            selectinload(PurchaseDemand.items).selectinload(PurchaseDemandItem.item).selectinload(Item.brand),
            selectinload(PurchaseDemand.project),
            selectinload(PurchaseDemand.creator),
            selectinload(PurchaseDemand.approver),
        )
        .filter(PurchaseDemand.id == demand_id)
        .first()
    )


def get_purchase_demand_item(
    db: Session, demand_item_id: int
) -> PurchaseDemandItem | None:
    return db.query(PurchaseDemandItem).filter(PurchaseDemandItem.id == demand_item_id).first()


# ── Update ────────────────────────────────────────────────────────────────────

def update_purchase_demand(
    db: Session,
    demand: PurchaseDemand,
    data: PurchaseDemandUpdate,
    updated_by: int,
) -> PurchaseDemand:
    if data.remarks is not None:
        demand.remarks = data.remarks

    demand.updated_by = updated_by

    if data.items is not None:
        # Replace all line items atomically
        db.query(PurchaseDemandItem).filter(
            PurchaseDemandItem.purchase_demand_id == demand.id
        ).delete(synchronize_session="fetch")
        for item_data in data.items:
            db.add(
                PurchaseDemandItem(
                    purchase_demand_id=demand.id,
                    item_id=item_data.item_id,
                    quantity=item_data.quantity,
                    notes=item_data.notes,
                )
            )

    db.commit()
    db.refresh(demand)
    return demand


def add_purchase_demand_item(
    db: Session,
    demand: PurchaseDemand,
    item_id: int,
    quantity: float,
    notes: str | None,
    updated_by: int,
) -> PurchaseDemand:
    db.add(
        PurchaseDemandItem(
            purchase_demand_id=demand.id,
            item_id=item_id,
            quantity=quantity,
            notes=notes,
        )
    )
    demand.updated_by = updated_by
    db.commit()
    db.refresh(demand)
    return demand


# ── Workflow transitions ──────────────────────────────────────────────────────

def submit_purchase_demand(
    db: Session, demand: PurchaseDemand, updated_by: int
) -> PurchaseDemand:
    demand.status = "pending_approval"
    demand.updated_by = updated_by
    db.commit()
    db.refresh(demand)
    return demand


def approve_purchase_demand(
    db: Session,
    demand: PurchaseDemand,
    approved_by: int,
    remarks: str | None = None,
) -> PurchaseDemand:
    demand.status = "approved"
    demand.approved_by = approved_by
    demand.approved_at = datetime.now(timezone.utc)
    if remarks is not None:
        demand.remarks = remarks
    db.commit()
    db.refresh(demand)
    return demand


def reject_purchase_demand(
    db: Session,
    demand: PurchaseDemand,
    rejected_by: int,
    remarks: str | None = None,
) -> PurchaseDemand:
    demand.status = "rejected"
    demand.updated_by = rejected_by
    if remarks is not None:
        demand.remarks = remarks
    db.commit()
    db.refresh(demand)
    return demand


def cancel_purchase_demand(
    db: Session, demand: PurchaseDemand, updated_by: int
) -> PurchaseDemand:
    demand.status = "cancelled"
    demand.updated_by = updated_by
    db.commit()
    db.refresh(demand)
    return demand


def delete_purchase_demand(db: Session, demand: PurchaseDemand) -> None:
    db.delete(demand)
    db.commit()


# ── Vendor suggestions ────────────────────────────────────────────────────────

def get_suggested_vendors_for_item(db: Session, item_id: int) -> list[Vendor]:
    """Return vendors matching the item by brand OR sub-category."""
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return []
    
    vendor_ids: set[int] = set()
    
    # 1. By Brand
    if item.brand_id:
        vendor_ids.update(
            vb.vendor_id
            for vb in db.query(VendorBrand)
            .filter(VendorBrand.brand_id == item.brand_id)
            .all()
        )
        
    # 2. By SubCategory -> Category -> VendorGroup
    if item.scat_id:
        scat = db.query(SubCategory).filter(SubCategory.id == item.scat_id).first()
        if scat and scat.cat_id:
            vendor_ids.update(
                vg.vendor_id
                for vg in db.query(VendorGroup)
                .filter(VendorGroup.cat_id == scat.cat_id)
                .all()
            )
            
    if not vendor_ids:
        return []
        
    return db.query(Vendor).filter(Vendor.id.in_(vendor_ids)).all()


def get_vendor_profiles_for_item(db: Session, item_id: int) -> list[dict]:
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        return []
    return get_vendors_for_item_model(db, item)


def get_vendors_for_item_model(db: Session, item) -> list[dict]:
    """
    Returns full vendor profiles for an item ORM object.
    Discovers vendors via:
      - Item.brand_id  → VendorBrand → Vendor
      - Item.scat_id   → SubCategory → Category → VendorGroup → Vendor
    """
    vendor_ids: set[int] = set()

    if item.brand_id:
        vendor_ids.update(
            vb.vendor_id
            for vb in db.query(VendorBrand)
            .filter(VendorBrand.brand_id == item.brand_id)
            .all()
        )

    if item.scat_id:
        scat = db.query(SubCategory).filter(SubCategory.id == item.scat_id).first()
        if scat and scat.cat_id:
            vendor_ids.update(
                vg.vendor_id
                for vg in db.query(VendorGroup)
                .filter(VendorGroup.cat_id == scat.cat_id)
                .all()
            )

    if not vendor_ids:
        return []

    vendors = db.query(Vendor).filter(Vendor.id.in_(vendor_ids)).all()
    results: list[dict] = []

    for vendor in vendors:
        contact = (
            db.query(VendorContactPerson)
            .filter(VendorContactPerson.vendor_id == vendor.id)
            .order_by(VendorContactPerson.id.asc())
            .first()
        )

        group_names = [
            vg.category.name
            for vg in db.query(VendorGroup)
            .filter(VendorGroup.vendor_id == vendor.id)
            .all()
            if vg.category and vg.category.name
        ]

        brand_names = [
            vb.brand.name
            for vb in db.query(VendorBrand)
            .filter(VendorBrand.vendor_id == vendor.id)
            .all()
            if vb.brand and vb.brand.name
        ]

        results.append(
            {
                "vendor_id": vendor.id,
                "vendor_name": vendor.name,
                "vendor_type": vendor.type,
                "vendor_group": sorted(set(group_names)),
                "contact_person": contact.name if contact else None,
                "contact_designation": contact.designation if contact else None,
                "phone": (contact.mobile if contact and contact.mobile else vendor.mobile),
                "email": vendor.email,
                "website": vendor.website,
                "address": vendor.address,
                "brands_supplied": sorted(set(brand_names)),
            }
        )

    return results


def assign_vendors_to_demand(
    db: Session,
    demand: PurchaseDemand,
    assignments: list, # List of PurchaseDemandItemVendorAssign objects (schemas)
    selected_by: int = None
) -> list[PurchaseDemandVendor]:
    """Replace the selected-vendor list for a demand with per-item assignments."""
    demand_col = _purchase_demand_vendor_has_demand_column(db)
    if not demand_col:
        return []

    # 1. Clear existing assignments
    filter_kwargs = {demand_col: demand.id}
    db.query(PurchaseDemandVendor).filter_by(**filter_kwargs).delete(synchronize_session="fetch")

    new_rows: list[PurchaseDemandVendor] = []
    
    # 2. Process each per-item assignment
    for assign in assignments:
        item_id = assign.item_id
        vendor_ids = assign.vendor_ids

        # Validate item belongs to demand
        demand_item = db.query(PurchaseDemandItem).filter(
            PurchaseDemandItem.id == item_id,
            PurchaseDemandItem.purchase_demand_id == demand.id
        ).first()
        if not demand_item:
            raise ValueError(f"Item ID {item_id} does not belong to demand {demand.demand_code}.")

        # Get allowed vendors for this specific item (brand/category match)
        item_model = db.query(Item).filter(Item.id == demand_item.item_id).first()
        allowed_profiles = get_vendors_for_item_model(db, item_model)
        allowed_ids = {p["vendor_id"] for p in allowed_profiles}

        # Check for invalid vendors for this item
        invalid = [v for v in vendor_ids if v not in allowed_ids]
        if invalid:
            raise ValueError(
                f"Vendor IDs {', '.join(map(str, invalid))} are not allowed for Item {item_model.name} (Category/Brand mismatch)."
            )

        # 3. Create the new assignments
        for v_id in vendor_ids:
            row_kwargs = {
                demand_col: demand.id,
                "purchase_demand_item_id": item_id,
                "vendor_id": v_id,
            }
            if selected_by is not None:
                row_kwargs["selected_by"] = selected_by
            row = PurchaseDemandVendor(**row_kwargs)
            db.add(row)
            new_rows.append(row)

    db.commit()
    for row in new_rows:
        db.refresh(row)
    return new_rows


def get_selected_vendors_for_demand(
    db: Session, demand_id: int
) -> list[PurchaseDemandVendor]:
    demand_col = _purchase_demand_vendor_has_demand_column(db)
    if not demand_col:
        return []

    filter_kwargs = {demand_col: demand_id}
    return (
        db.query(PurchaseDemandVendor)
        .filter_by(**filter_kwargs)
        .order_by(PurchaseDemandVendor.id.asc())
        .all()
    )


def has_selected_vendors_for_demand(db: Session, demand_id: int) -> bool:
    demand_col = _purchase_demand_vendor_has_demand_column(db)
    if not demand_col:
        return False

    filter_kwargs = {demand_col: demand_id}
    count = (
        db.query(PurchaseDemandVendor)
        .filter_by(**filter_kwargs)
        .count()
    )
    return count > 0
