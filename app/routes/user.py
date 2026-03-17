from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.dependencies import get_db, get_admin_user
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.crud import user as user_crud

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    existing_email = user_crud.get_user_by_email(db, data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A user with email '{data.email}' already exists."
        )
    existing_username = user_crud.get_user_by_username(db, data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A user with username '{data.username}' already exists."
        )
    return user_crud.create_user(db, data)


@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    users = user_crud.get_users(db)
    if not users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No users found."
        )
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="user_id must be a positive integer."
        )
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, data: UserUpdate, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="user_id must be a positive integer."
        )
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )
    if data.email:
        duplicate = user_crud.get_user_by_email(db, data.email)
        if duplicate and duplicate.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Another user with email '{data.email}' already exists."
            )
    if data.username:
        duplicate = user_crud.get_user_by_username(db, data.username)
        if duplicate and duplicate.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Another user with username '{data.username}' already exists."
            )
    return user_crud.update_user(db, user_id, data)


@router.delete("/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int, db: Session = Depends(get_db), current_user=Depends(get_admin_user)):
    if user_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="user_id must be a positive integer."
        )
    user = user_crud.get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with id {user_id} not found."
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account."
        )
    user_crud.delete_user(db, user_id)
    return {"message": f"User '{user.username}' deleted successfully."}