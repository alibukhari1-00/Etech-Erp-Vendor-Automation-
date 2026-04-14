from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_admin_user
from app.crud import system_setting as setting_crud
from app.schemas.system_setting import PurchaserAccessSettingResponse, PurchaserAccessSettingUpdate

router = APIRouter(prefix="/settings", tags=["System Settings"])


@router.get("/purchaser-access", response_model=PurchaserAccessSettingResponse)
def get_purchaser_access_setting(
    db: Session = Depends(get_db),
    _current_user=Depends(get_admin_user),
):
    enabled = setting_crud.get_purchaser_access_enabled(db)
    return PurchaserAccessSettingResponse(purchaser_access_enabled=enabled)


@router.put("/purchaser-access", response_model=PurchaserAccessSettingResponse)
def update_purchaser_access_setting(
    data: PurchaserAccessSettingUpdate,
    db: Session = Depends(get_db),
    _current_user=Depends(get_admin_user),
):
    enabled = setting_crud.set_purchaser_access_enabled(db, data.purchaser_access_enabled)
    return PurchaserAccessSettingResponse(purchaser_access_enabled=enabled)
