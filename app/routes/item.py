from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.dependencies import get_db
from app.schemas.item import ItemCreate, ItemResponse, ItemEnrichedResponse, ItemSearchResult
from app.crud import item as crud
from app.crud import purchase_demand as pd_crud
from app.schemas.purchase_demand import VendorLookupResponse

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("/", response_model=ItemResponse, status_code=status.HTTP_201_CREATED)
def create_item(data: ItemCreate, db: Session = Depends(get_db)):
    if not crud.get_brand(db, data.brand_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with id {data.brand_id} does not exist."
        )
    if not crud.get_scat(db, data.scat_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sub-category with id {data.scat_id} does not exist."
        )
    return crud.create_item(db, data)


@router.get("/", response_model=list[ItemEnrichedResponse])
def get_items(db: Session = Depends(get_db)):
    items = crud.get_items(db)  # uses joinedload for brand + sub_category
    if not items:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No items found."
        )
    result = []
    for it in items:
        data = ItemEnrichedResponse.model_validate(it)
        data.brand_name = it.brand.name if it.brand else None
        data.scat_name = it.sub_category.name if it.sub_category else None
        result.append(data)
    return result


@router.get("/search", response_model=list[ItemSearchResult])
def search_items(
    q: str = Query(..., min_length=1, description="Search term"),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    rows = crud.search_items(db, q=q, limit=limit)
    return rows


@router.get("/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    if item_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="item_id must be a positive integer."
        )
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found."
        )
    return item


@router.get("/{item_id}/vendors", response_model=list[VendorLookupResponse])
def get_item_vendors(item_id: int, db: Session = Depends(get_db)):
    if item_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="item_id must be a positive integer."
        )

    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found."
        )

    return pd_crud.get_vendor_profiles_for_item(db, item_id)


@router.put("/{item_id}", response_model=ItemResponse)
def update_item(item_id: int, data: ItemCreate, db: Session = Depends(get_db)):
    if item_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="item_id must be a positive integer."
        )
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found."
        )
    if not crud.get_brand(db, data.brand_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Brand with id {data.brand_id} does not exist."
        )
    if not crud.get_scat(db, data.scat_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sub-category with id {data.scat_id} does not exist."
        )
    return crud.update_item(db, item_id, data)


@router.delete("/{item_id}", status_code=status.HTTP_200_OK)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    if item_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="item_id must be a positive integer."
        )
    item = crud.get_item(db, item_id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with id {item_id} not found."
        )
    crud.delete_item(db, item_id)
    return {"message": f"Item with id {item_id} deleted successfully."}