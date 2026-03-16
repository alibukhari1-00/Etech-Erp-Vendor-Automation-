from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import engine, Base
from app.models import (
    Location, Brand, Category, SubCategory, Item,
    Vendor, VendorGroup, VendorBrand, VendorContactPerson, User
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
from app.routes import auth, user, dashboard

app = FastAPI(
    title="ETSolar ERP API",
    description="Enterprise Resource Planning API for ETSolar",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Auth & User routes
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(dashboard.router)

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