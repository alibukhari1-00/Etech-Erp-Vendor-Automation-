from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.dependencies import get_db
from app.schemas.subcategory import SubCategoryCreate, SubCategoryResponse
from app.crud import subcategory as crud

router = APIRouter(prefix="/subcategories", tags=["SubCategories"])


@router.post("/", response_model=SubCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_subcategory(data: SubCategoryCreate, db: Session = Depends(get_db)):
    if not crud.get_category(db, data.cat_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {data.cat_id} does not exist."
        )
    existing = crud.get_subcategory_by_name(db, data.name, data.cat_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A sub-category named '{data.name}' already exists under category {data.cat_id}."
        )
    return crud.create_subcategory(db, data)


@router.get("/", response_model=list[SubCategoryResponse])
def get_subcategories(db: Session = Depends(get_db)):
    subcategories = crud.get_subcategories(db)
    if not subcategories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No sub-categories found."
        )
    return subcategories


@router.get("/{sub_id}", response_model=SubCategoryResponse)
def get_subcategory(sub_id: int, db: Session = Depends(get_db)):
    if sub_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="sub_id must be a positive integer."
        )
    subcategory = crud.get_subcategory(db, sub_id)
    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sub-category with id {sub_id} not found."
        )
    return subcategory


@router.put("/{sub_id}", response_model=SubCategoryResponse)
def update_subcategory(sub_id: int, data: SubCategoryCreate, db: Session = Depends(get_db)):
    if sub_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="sub_id must be a positive integer."
        )
    subcategory = crud.get_subcategory(db, sub_id)
    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sub-category with id {sub_id} not found."
        )
    if not crud.get_category(db, data.cat_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Category with id {data.cat_id} does not exist."
        )
    duplicate = crud.get_subcategory_by_name(db, data.name, data.cat_id)
    if duplicate and duplicate.id != sub_id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Another sub-category named '{data.name}' already exists under category {data.cat_id}."
        )
    return crud.update_subcategory(db, sub_id, data)


@router.delete("/{sub_id}", status_code=status.HTTP_200_OK)
def delete_subcategory(sub_id: int, db: Session = Depends(get_db)):
    if sub_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="sub_id must be a positive integer."
        )
    subcategory = crud.get_subcategory(db, sub_id)
    if not subcategory:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sub-category with id {sub_id} not found."
        )
    crud.delete_subcategory(db, sub_id)
    return {"message": f"Sub-category '{subcategory.name}' deleted successfully."}