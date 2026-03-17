from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base


class PurchaseDemand(Base):
    __tablename__ = "purchase_demands"

    id = Column(Integer, primary_key=True, index=True)
    demand_code = Column(String, unique=True, index=True, nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    status = Column(
        Enum(
            "draft",
            "pending_approval",
            "approved",
            "rejected",
            "cancelled",
            name="demand_status",
        ),
        default="draft",
        nullable=False,
    )
    remarks = Column(Text, nullable=True)

    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    project = relationship("Project", back_populates="purchase_demands")
    creator = relationship("User", foreign_keys=[created_by])
    updater = relationship("User", foreign_keys=[updated_by])
    approver = relationship("User", foreign_keys=[approved_by])
    items = relationship(
        "PurchaseDemandItem",
        back_populates="demand",
        cascade="all, delete-orphan",
    )
    selected_vendors = relationship(
        "PurchaseDemandVendor",
        back_populates="demand",
        cascade="all, delete-orphan",
    )
