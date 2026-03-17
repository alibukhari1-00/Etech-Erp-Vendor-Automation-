from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    project_code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    location_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    status = Column(
        Enum("active", "completed", "closed", name="project_status"),
        default="active",
        nullable=False,
    )
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    location = relationship("Location")
    creator = relationship("User", foreign_keys=[created_by])
    purchase_demands = relationship("PurchaseDemand", back_populates="project")
