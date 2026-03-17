from sqlalchemy.orm import Session
from app.models.log import Log


def add_log(db: Session, project_id: int, status: str) -> Log:
    entry = Log(project_id=project_id, status=status[:255])
    try:
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    except Exception:
        db.rollback()
        return entry
