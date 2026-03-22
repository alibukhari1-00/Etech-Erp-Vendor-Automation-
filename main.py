from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from app.db.database import engine, Base
from app.models import (
    Location, Brand, Category, SubCategory, Item,
    Vendor, VendorGroup, VendorBrand, VendorContactPerson, User, SystemSetting,
    Project, PurchaseDemand, PurchaseDemandItem, PurchaseDemandVendor, PurchaseQuotation, Log,
)

from app.routes import (
    vendor,
    brand,
    location,
    category,
    subcategory,
    item,
    vendor_group,
    vendor_brand,
    vendor_contact_person
)
from app.routes import auth, user, dashboard, system_setting, project, purchase_demand, purchase_quotation
from app.routes import ai_chat

app = FastAPI(
    title="ETSolar ERP API",
    description="Enterprise Resource Planning API for ETSolar",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)


def _ensure_users_profile_columns() -> None:
    inspector = inspect(engine)
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "avatar_url" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE users ADD COLUMN avatar_url VARCHAR"))


_ensure_users_profile_columns()

# Keep enum values aligned in existing PostgreSQL databases.
if engine.dialect.name == "postgresql":
    with engine.begin() as connection:
        connection.execute(text("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'purchaser'"))

# Auth & User routes
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(dashboard.router)
app.include_router(system_setting.router)

# Entity routes
app.include_router(vendor.router)
app.include_router(brand.router)
app.include_router(location.router)
app.include_router(category.router)
app.include_router(subcategory.router)
app.include_router(item.router)
app.include_router(vendor_group.router)
app.include_router(vendor_brand.router)
app.include_router(vendor_contact_person.router)
app.include_router(project.router)
app.include_router(purchase_demand.router)
app.include_router(purchase_quotation.router)
app.include_router(ai_chat.router)
