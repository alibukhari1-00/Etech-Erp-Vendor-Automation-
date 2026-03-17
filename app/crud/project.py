from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def _next_project_code(db: Session) -> str:
    last = db.query(Project).order_by(Project.id.desc()).first()
    next_num = (last.id + 1) if last else 1
    return f"PRJ-{next_num:04d}"


def create_project(db: Session, data: ProjectCreate, created_by: int) -> Project:
    project = Project(
        project_code=_next_project_code(db),
        name=data.name,
        location_id=data.location_id,
        status=data.status,
        created_by=created_by,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_projects(db: Session) -> list[Project]:
    return db.query(Project).order_by(Project.id.desc()).all()


def get_project(db: Session, project_id: int) -> Project | None:
    return db.query(Project).filter(Project.id == project_id).first()


def get_project_by_code(db: Session, code: str) -> Project | None:
    return db.query(Project).filter(Project.project_code == code).first()


def update_project(db: Session, project: Project, data: ProjectUpdate) -> Project:
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(project, key, value)
    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: Project) -> None:
    db.delete(project)
    db.commit()
