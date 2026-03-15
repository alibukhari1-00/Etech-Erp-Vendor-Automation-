from fastapi import FastAPI

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

app = FastAPI()

app.include_router(vendor.router)
app.include_router(brand.router)
app.include_router(location.router)
app.include_router(category.router)
app.include_router(subcategory.router)
app.include_router(item.router)
app.include_router(vendor_group.router)
app.include_router(vendor_brand.router)
app.include_router(vendor_contact_person.router)