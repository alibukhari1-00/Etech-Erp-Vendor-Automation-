from pydantic import BaseModel


class PurchaserAccessSettingResponse(BaseModel):
    purchaser_access_enabled: bool


class PurchaserAccessSettingUpdate(BaseModel):
    purchaser_access_enabled: bool
