from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_current_user, get_admin_user
from app.models.user import User
from app.models.item import Item
from app.models.brand import Brand
from app.models.subcategory import SubCategory
from app.models.project import Project
from app.schemas.purchase_demand import (
    PurchaseDemandCreate,
    PurchaseDemandUpdate,
    PurchaseDemandItemCreate,
    PurchaseDemandVendorAssign,
    PurchaseDemandResponse,
    PurchaseDemandItemResponse,
    SelectedVendorResponse,
    ProjectSummary,
    UserSummary,
    ItemBrief,
    ApproveRequest,
    RejectRequest,
    QuotationVendorEntry,
)
from app.crud import purchase_demand as pd_crud
from app.crud import log as log_crud

router = APIRouter(prefix="/purchase-demands", tags=["Purchase Demands"])

LOCKED_STATUSES = {"approved", "rejected", "cancelled"}


# ── Helper: enrich demand with vendor suggestions ─────────────────────────────

def _enrich(
    db: Session,
    demand,
    include_suggested_vendors: bool = True,
    include_selected_vendors: bool = True,
) -> PurchaseDemandResponse:
    brand_ids = {
        di.item.brand_id
        for di in demand.items
        if di.item and di.item.brand_id is not None
    }
    scat_ids = {
        di.item.scat_id
        for di in demand.items
        if di.item and di.item.scat_id is not None
    }

    brand_map = {
        row.id: row.name
        for row in db.query(Brand).filter(Brand.id.in_(brand_ids)).all()
    } if brand_ids else {}
    scat_map = {
        row.id: row.name
        for row in db.query(SubCategory).filter(SubCategory.id.in_(scat_ids)).all()
    } if scat_ids else {}

    items_enriched = []
    for di in demand.items:
        vendors = pd_crud.get_suggested_vendors_for_item(db, di.item_id) if include_suggested_vendors else []
        
        # ── Item Enrichment & Self-Healing Logic ──
        item_brief = None
        if di.item:
            # Resolve Brand Name (Map -> Object -> Fallback)
            b_name = brand_map.get(di.item.brand_id) or (di.item.brand.name if di.item.brand else "Generic Brand")
            # Resolve Sub-Category Name (Map -> Object -> Fallback)
            s_name = scat_map.get(di.item.scat_id) or (di.item.sub_category.name if di.item.sub_category else "Uncategorized")
            
            item_brief = ItemBrief(
                id=di.item.id,
                brand_id=di.item.brand_id,
                brand_name=b_name,
                scat_id=di.item.scat_id,
                scat_name=s_name,
                power_rating_kv=di.item.power_rating_kv,
                voltage=di.item.voltage,
                ip_rating=di.item.ip_rating,
                uom=di.item.uom,
                purchase_rate=di.item.purchase_rate,
                sale_rate=di.item.sale_rate,
            )
        else:
            # DATA SELF-HEALING: If item record is missing (e.g. legacy/corrupt), 
            # we use 'notes' as the primary descriptive field to avoid "Unknown" errors.
            item_brief = ItemBrief(
                id=di.item_id,
                brand_name="Generic",
                scat_name=di.notes or f"Manual Item ({di.item_id})",
                uom="units"
            )
        
        items_enriched.append(
            PurchaseDemandItemResponse(
                id=di.id,
                purchase_demand_id=di.purchase_demand_id,
                item_id=di.item_id,
                quantity=di.quantity,
                notes=di.notes,
                item=item_brief,
                suggested_vendors=vendors,
            )
        )

    selected_vendors = pd_crud.get_selected_vendors_for_demand(db, demand.id) if include_selected_vendors else []

    return PurchaseDemandResponse(
        id=demand.id,
        demand_code=demand.demand_code,
        project_id=demand.project_id,
        status=demand.status,
        remarks=demand.remarks,
        created_by=demand.created_by,
        updated_by=demand.updated_by,
        approved_by=demand.approved_by,
        approved_at=demand.approved_at,
        created_at=demand.created_at,
        updated_at=demand.updated_at,
        project=(
            ProjectSummary(
                id=demand.project.id,
                project_code=demand.project.project_code,
                name=demand.project.name,
            ) if demand.project else None
        ),
        created_by_user=(
            UserSummary(
                id=demand.creator.id,
                full_name=demand.creator.full_name,
                username=demand.creator.username,
            ) if demand.creator else None
        ),
        approved_by_user=(
            UserSummary(
                id=demand.approver.id,
                full_name=demand.approver.full_name,
                username=demand.approver.username,
            ) if demand.approver else None
        ),
        selected_vendors=[
            SelectedVendorResponse(
                id=row.id,
                purchase_demand_id=row.purchase_demand_id,
                purchase_demand_item_id=row.purchase_demand_item_id,
                vendor_id=row.vendor_id,
                vendor_name=row.vendor.name if row.vendor else None,
            )
            for row in selected_vendors
        ],
        items=items_enriched,
    )


def _enrich_list_row(db: Session, demand) -> PurchaseDemandResponse:
    # Use the full enrichment for list as well, to support direct approval wizards on Dashboard
    return _enrich(db, demand, include_suggested_vendors=True, include_selected_vendors=True)


def _get_demand_or_404(db: Session, demand_id: int):
    demand = pd_crud.get_purchase_demand(db, demand_id)
    if not demand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Purchase demand with id {demand_id} not found.",
        )
    return demand


def _assert_editable(demand):
    if demand.status in LOCKED_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Demand '{demand.demand_code}' is {demand.status} and cannot be modified.",
        )


# ── Create ────────────────────────────────────────────────────────────────────

@router.post("/", response_model=PurchaseDemandResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_demand(
    data: PurchaseDemandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        project = db.query(Project).filter(Project.id == data.project_id).first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with id {data.project_id} not found.",
            )
        if project.status in ("completed", "closed"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Cannot create a purchase demand for a {project.status} project.",
            )

        # Validate all item IDs exist
        for line in data.items:
            if not db.query(Item).filter(Item.id == line.item_id).first():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item with id {line.item_id} not found.",
                )

        demand = pd_crud.create_purchase_demand(db, data, current_user.id)
        log_crud.add_log(db, demand.project_id, f"Purchase demand {demand.demand_code} saved")
        return _enrich(db, demand)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to create demand.")


# ── List ──────────────────────────────────────────────────────────────────────

@router.get("/", response_model=list[PurchaseDemandResponse])
def get_purchase_demands(
    project_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    demands = pd_crud.get_purchase_demands(db, project_id=project_id)
    if current_user.role == "admin":
        # Admin sees only submitted demands raised by non-admin users.
        demands = [
            d
            for d in demands
            if d.status == "pending_approval"
            and d.creator
            and d.creator.role != "admin"
        ]
    if current_user.role == "purchaser":
        demands = [d for d in demands if d.created_by == current_user.id]
    return [_enrich_list_row(db, d) for d in demands]


# ── Detail ────────────────────────────────────────────────────────────────────

@router.get("/{demand_id}", response_model=PurchaseDemandResponse)
def get_purchase_demand(
    demand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    demand = _get_demand_or_404(db, demand_id)
    if current_user.role == "admin":
        is_non_admin_creator = bool(demand.creator and demand.creator.role != "admin")
        if not (demand.status == "pending_approval" and is_non_admin_creator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins can only access submitted demands from non-admin users.",
            )
    if current_user.role == "purchaser" and demand.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own purchase demands.",
        )
    return _enrich(db, demand)


@router.post("/{demand_id}/items", response_model=PurchaseDemandResponse)
def add_purchase_demand_item(
    demand_id: int,
    data: PurchaseDemandItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    demand = _get_demand_or_404(db, demand_id)

    if demand.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Items can only be added while demand is in draft status.",
        )
    if current_user.role == "purchaser" and demand.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own purchase demands.",
        )

    item = db.query(Item).filter(Item.id == data.item_id).first()
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {data.item_id} not found.",
        )

    updated = pd_crud.add_purchase_demand_item(
        db,
        demand,
        item_id=data.item_id,
        quantity=data.quantity,
        notes=data.notes,
        updated_by=current_user.id,
    )
    log_crud.add_log(db, demand.project_id, f"Item {data.item_id} added to demand {demand.demand_code}")
    return _enrich(db, updated)


# ── Update ────────────────────────────────────────────────────────────────────

@router.put("/{demand_id}", response_model=PurchaseDemandResponse)
def update_purchase_demand(
    demand_id: int,
    data: PurchaseDemandUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    demand = _get_demand_or_404(db, demand_id)
    _assert_editable(demand)

    # Purchaser can only edit their own demands
    if current_user.role == "purchaser" and demand.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own purchase demands.",
        )

    if data.items is not None:
        for line in data.items:
            if not db.query(Item).filter(Item.id == line.item_id).first():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item with id {line.item_id} not found.",
                )

    updated = pd_crud.update_purchase_demand(db, demand, data, current_user.id)
    return _enrich(db, updated)


# ── Submit for approval ───────────────────────────────────────────────────────

@router.post("/{demand_id}/submit", response_model=PurchaseDemandResponse)
def submit_purchase_demand(
    demand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    demand = _get_demand_or_404(db, demand_id)

    if demand.status != "draft":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only draft demands can be submitted. Current status: {demand.status}.",
        )
    if current_user.role == "purchaser" and demand.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only submit your own purchase demands.",
        )

    updated = pd_crud.submit_purchase_demand(db, demand, current_user.id)
    log_crud.add_log(db, demand.project_id, f"Demand {demand.demand_code} submitted for approval")
    return _enrich(db, updated)


@router.get("/{demand_id}/vendors", response_model=list[SelectedVendorResponse])
def get_selected_vendors_for_demand(
    demand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    demand = _get_demand_or_404(db, demand_id)
    if current_user.role == "purchaser" and demand.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own purchase demands.",
        )

    rows = pd_crud.get_selected_vendors_for_demand(db, demand_id)
    return [
        SelectedVendorResponse(
            id=row.id,
            purchase_demand_id=row.purchase_demand_id,
            purchase_demand_item_id=row.purchase_demand_item_id,
            vendor_id=row.vendor_id,
            vendor_name=row.vendor.name if row.vendor else None,
        )
        for row in rows
    ]


@router.post("/{demand_id}/vendors", response_model=list[SelectedVendorResponse])
def select_vendors_for_demand(
    demand_id: int,
    body: PurchaseDemandVendorAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    demand = _get_demand_or_404(db, demand_id)
    if demand.status not in ("draft", "pending_approval"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot select vendors when demand status is {demand.status}.",
        )

    try:
        rows = pd_crud.assign_vendors_to_demand(db, demand=demand, assignments=body.assignments, selected_by=current_user.id)
    except ValueError as ex:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ex))

    log_crud.add_log(
        db,
        demand.project_id,
        f"Per-item vendors selected for demand {demand.demand_code}",
    )

    return [
        SelectedVendorResponse(
            id=row.id,
            purchase_demand_id=row.purchase_demand_id,
            purchase_demand_item_id=row.purchase_demand_item_id,
            vendor_id=row.vendor_id,
            vendor_name=row.vendor.name if row.vendor else None,
        )
        for row in rows
    ]


# ── Approve (admin only) ──────────────────────────────────────────────────────

@router.post("/{demand_id}/approve", response_model=PurchaseDemandResponse)

def approve_purchase_demand(
    demand_id: int,
    body: ApproveRequest = ApproveRequest(),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    demand = _get_demand_or_404(db, demand_id)

    if demand.status != "pending_approval":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Only pending_approval demands can be approved. Current status: {demand.status}.",
        )

    if not demand.items:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot approve an empty purchase demand.",
        )

    # DEBUG: Log vendor assignment count before approval check
    vendor_count = db.query(pd_crud.PurchaseDemandVendor).filter(pd_crud.PurchaseDemandVendor.purchase_demand_id == demand.id).count()
    print(f"[DEBUG] Vendor assignments for demand {demand.id}: {vendor_count}")

    if not pd_crud.has_selected_vendors_for_demand(db, demand.id):
        print(f"[DEBUG] No vendor assignments found for demand {demand.id} at approval time.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Select at least one vendor for this purchase demand before approval.",
        )

    updated = pd_crud.approve_purchase_demand(db, demand, current_user.id, body.remarks)
    log_crud.add_log(db, demand.project_id, f"Demand {demand.demand_code} approved")
    return _enrich(db, updated)


# ── Reject (admin only) ───────────────────────────────────────────────────────

@router.post("/{demand_id}/reject", response_model=PurchaseDemandResponse)
def reject_purchase_demand(
    demand_id: int,
    body: RejectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    demand = _get_demand_or_404(db, demand_id)

    if demand.status not in ("pending_approval", "draft"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot reject a demand with status: {demand.status}.",
        )

    updated = pd_crud.reject_purchase_demand(db, demand, current_user.id, body.remarks)
    return _enrich(db, updated)


# ── Cancel ────────────────────────────────────────────────────────────────────

@router.post("/{demand_id}/cancel", response_model=PurchaseDemandResponse)
def cancel_purchase_demand(
    demand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    demand = _get_demand_or_404(db, demand_id)
    _assert_editable(demand)

    if current_user.role == "purchaser" and demand.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own purchase demands.",
        )

    updated = pd_crud.cancel_purchase_demand(db, demand, current_user.id)
    return _enrich(db, updated)


# ── Delete (hard delete — admin only, draft/cancelled only) ───────────────────

@router.delete("/{demand_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_purchase_demand(
    demand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    demand = _get_demand_or_404(db, demand_id)

    if demand.status not in ("draft", "cancelled"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft or cancelled demands can be permanently deleted.",
        )

    pd_crud.delete_purchase_demand(db, demand)
    if demand.status not in ("draft", "cancelled"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only draft or cancelled demands can be permanently deleted.",
        )

    pd_crud.delete_purchase_demand(db, demand)


# ── Quotation candidates (admin only) ─────────────────────────────────────────

@router.get("/{demand_id}/quotation-candidates", response_model=list[QuotationVendorEntry])
def get_quotation_candidates(
    demand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_admin_user),
):
    """
    Return all vendors (by brand + category) that match any item in this demand.
    Used by admin to select who receives a purchase quotation.
    """
    demand = _get_demand_or_404(db, demand_id)

    vendor_map: dict[int, dict] = {}
    for di in demand.items:
        if not di.item:
            continue
        profiles = pd_crud.get_vendors_for_item_model(db, di.item)
        for profile in profiles:
            vid = profile["vendor_id"]
            if vid not in vendor_map:
                vendor_map[vid] = {**profile, "item_ids": []}
            if di.item_id not in vendor_map[vid]["item_ids"]:
                vendor_map[vid]["item_ids"].append(di.item_id)

    return [QuotationVendorEntry(**v) for v in vendor_map.values()]
