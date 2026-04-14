from sqlalchemy.orm import Session
from app.models.system_setting import SystemSetting

PURCHASER_ACCESS_KEY = "purchaser_access_enabled"


def get_purchaser_access_enabled(db: Session) -> bool:
    row = db.query(SystemSetting).filter(SystemSetting.key == PURCHASER_ACCESS_KEY).first()
    if not row:
        return False
    return str(row.value).strip().lower() == "true"


def set_purchaser_access_enabled(db: Session, enabled: bool) -> bool:
    row = db.query(SystemSetting).filter(SystemSetting.key == PURCHASER_ACCESS_KEY).first()
    value = "true" if enabled else "false"
    if row:
        row.value = value
    else:
        row = SystemSetting(key=PURCHASER_ACCESS_KEY, value=value)
        db.add(row)
    db.commit()
    return enabled
