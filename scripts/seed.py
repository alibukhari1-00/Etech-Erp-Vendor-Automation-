"""
ETSolar ERP - Database Seed Script

Creates initial admin user and sample data for all entities.
Run: python -m scripts.seed  (from backend/)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from app.db.database import SessionLocal, engine, Base
from app.models.user import User
from app.models.location import Location
from app.models.category import Category
from app.models.subcategory import SubCategory
from app.models.brand import Brand
from app.models.item import Item
from app.models.vendor import Vendor
from app.models.vendor_contact_person import VendorContactPerson
from app.models.vendor_group import VendorGroup
from app.models.vendor_brand import VendorBrand
from app.core.security import hash_password


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # ── Admin User ─────────────────────────────────────────
        if not db.query(User).filter(User.email == "admin@etsolar.com").first():
            admin = User(
                email="admin@etsolar.com",
                username="admin",
                hashed_password=hash_password("Admin@123"),
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin)
            db.commit()
            print("✓ Admin user created (admin@etsolar.com / Admin@123)")
        else:
            print("• Admin user already exists")

        # ── Locations ──────────────────────────────────────────
        locations_data = [
            "Lahore", "Karachi", "Islamabad", "Faisalabad", "Multan"
        ]
        locations = {}
        for name in locations_data:
            loc = db.query(Location).filter(Location.loc_name == name).first()
            if not loc:
                loc = Location(loc_name=name)
                db.add(loc)
                db.commit()
                db.refresh(loc)
            locations[name] = loc
        print(f"✓ {len(locations)} locations seeded")

        # ── Categories ─────────────────────────────────────────
        categories_data = [
            "Solar Panels", "Solar Inverters", "Energy Storage",
            "Mounting Structures", "Security Systems"
        ]
        categories = {}
        for name in categories_data:
            cat = db.query(Category).filter(Category.name == name).first()
            if not cat:
                cat = Category(name=name)
                db.add(cat)
                db.commit()
                db.refresh(cat)
            categories[name] = cat
        print(f"✓ {len(categories)} categories seeded")

        # ── SubCategories ──────────────────────────────────────
        subcategories_data = [
            ("Mono PERC Panels", "Solar Panels"),
            ("Poly Crystalline Panels", "Solar Panels"),
            ("On-Grid Inverters", "Solar Inverters"),
            ("Hybrid Inverters", "Solar Inverters"),
            ("Off-Grid Inverters", "Solar Inverters"),
            ("Lithium Batteries", "Energy Storage"),
            ("Lead Acid Batteries", "Energy Storage"),
            ("L-Feet Mounts", "Mounting Structures"),
            ("Rail Mounts", "Mounting Structures"),
            ("CCTV Cameras", "Security Systems"),
        ]
        subcategories = {}
        for name, cat_name in subcategories_data:
            scat = db.query(SubCategory).filter(
                SubCategory.name == name,
                SubCategory.cat_id == categories[cat_name].id
            ).first()
            if not scat:
                scat = SubCategory(name=name, cat_id=categories[cat_name].id)
                db.add(scat)
                db.commit()
                db.refresh(scat)
            subcategories[name] = scat
        print(f"✓ {len(subcategories)} subcategories seeded")

        # ── Brands ─────────────────────────────────────────────
        brands_data = [
            ("Jinko Solar", "Jinko Solar Co Ltd", "Lahore", "active"),
            ("Longi Green", "Longi Green Energy", "Karachi", "active"),
            ("Huawei", "Huawei Technologies", "Islamabad", "active"),
            ("GoodWe", "GoodWe Power Supply", "Lahore", "active"),
            ("BYD", "BYD Company Ltd", "Faisalabad", "active"),
        ]
        brands = {}
        for name, company, loc_name, st in brands_data:
            brand = db.query(Brand).filter(Brand.name == name).first()
            if not brand:
                brand = Brand(
                    name=name, company=company,
                    loc_id=locations[loc_name].id, status=st
                )
                db.add(brand)
                db.commit()
                db.refresh(brand)
            brands[name] = brand
        print(f"✓ {len(brands)} brands seeded")

        # ── Items ──────────────────────────────────────────────
        items_data = [
            ("Mono PERC Panels", "Jinko Solar", 0.585, 48.0, "IP67", "pcs", 15000, 15, 17250, None),
            ("Mono PERC Panels", "Longi Green", 0.550, 41.7, "IP68", "pcs", 14500, 12, 16240, None),
            ("Poly Crystalline Panels", "Jinko Solar", 0.335, 38.5, "IP67", "pcs", 9800, 18, 11564, None),
            ("On-Grid Inverters", "Huawei", 10.0, 380.0, "IP65", "pcs", 185000, 20, 222000, None),
            ("On-Grid Inverters", "GoodWe", 8.0, 380.0, "IP65", "pcs", 145000, 18, 171100, None),
            ("Hybrid Inverters", "Huawei", 6.0, 230.0, "IP65", "pcs", 220000, 22, 268400, None),
            ("Hybrid Inverters", "GoodWe", 5.0, 230.0, "IP65", "pcs", 165000, 20, 198000, None),
            ("Off-Grid Inverters", "GoodWe", 3.0, 230.0, "IP20", "pcs", 85000, 15, 97750, None),
            ("Lithium Batteries", "BYD", 13.8, 51.2, "IP55", "pcs", 320000, 25, 400000, None),
            ("Lithium Batteries", "Huawei", 10.0, 51.2, "IP55", "pcs", 280000, 22, 341600, None),
            ("Lead Acid Batteries", "BYD", 0.2, 12.0, "IP20", "pcs", 35000, 15, 40250, None),
            ("L-Feet Mounts", "Jinko Solar", None, None, None, "set", 1200, 30, 1560, None),
            ("Rail Mounts", "Jinko Solar", None, None, None, "set", 2500, 25, 3125, None),
            ("CCTV Cameras", "Huawei", None, 12.0, "IP67", "pcs", 8500, 35, 11475, None),
            ("CCTV Cameras", "BYD", None, 12.0, "IP66", "pcs", 5200, 30, 6760, None),
        ]
        item_count = 0
        for scat_name, brand_name, power, volt, ip, uom, pr, pp, sr, srm in items_data:
            existing = db.query(Item).filter(
                Item.scat_id == subcategories[scat_name].id,
                Item.brand_id == brands[brand_name].id,
                Item.purchase_rate == pr
            ).first()
            if not existing:
                item = Item(
                    scat_id=subcategories[scat_name].id,
                    brand_id=brands[brand_name].id,
                    power_rating_kv=power,
                    voltage=volt,
                    ip_rating=ip,
                    uom=uom,
                    purchase_rate=pr,
                    profit_percentage=pp,
                    sale_rate=sr,
                    sale_rate_manual=srm,
                )
                db.add(item)
                item_count += 1
        db.commit()
        print(f"✓ {item_count} items seeded")

        # ── Vendors ────────────────────────────────────────────
        vendors_data = [
            ("SolarTech Imports", "+923001234567", "info@solartech.pk", "www.solartech.pk", "Main Blvd, Gulberg, Lahore", "Importer", "Whatsapp", "Lahore", "SolarTech Group"),
            ("Green Energy Traders", "+923009876543", "sales@greenenergy.com", "www.greenenergy.com", "I-8 Markaz, Islamabad", "Trader", "Email", "Islamabad", "Green Traders"),
            ("PowerMax Solutions", "+923111234567", "contact@powermax.pk", None, "Korangi Industrial, Karachi", "WholeSeller", "Call", "Karachi", "PowerMax WA"),
            ("SunRise EPC", "+923215556677", "info@sunrise-epc.com", "www.sunrise-epc.com", "Canal Road, Faisalabad", "EPC", "Portal", "Faisalabad", None),
            ("ElectroPak Store", "+923331112233", "electropak@gmail.com", None, "Anarkali, Lahore", "Shopkeeper", "Personal", "Lahore", None),
        ]
        vendors = {}
        for name, mobile, email, website, addr, vtype, source, loc_name, wag in vendors_data:
            vendor = db.query(Vendor).filter(Vendor.mobile == mobile).first()
            if not vendor:
                vendor = Vendor(
                    name=name, mobile=mobile, email=email,
                    website=website, address=addr, type=vtype,
                    source=source, loc_id=locations[loc_name].id,
                    whatsapp_group=wag
                )
                db.add(vendor)
                db.commit()
                db.refresh(vendor)
            vendors[name] = vendor
        print(f"✓ {len(vendors)} vendors seeded")

        # ── Vendor Contact Persons ─────────────────────────────
        contacts_data = [
            ("SolarTech Imports", "Ahmed Khan", "+923001234568", "Sales Manager"),
            ("SolarTech Imports", "Ali Raza", "+923001234569", "Procurement Head"),
            ("Green Energy Traders", "Hassan Malik", "+923009876544", "Director"),
            ("PowerMax Solutions", "Usman Shah", "+923111234568", "Operations Manager"),
            ("SunRise EPC", "Bilal Ahmed", "+923215556678", "Project Lead"),
            ("ElectroPak Store", "Nawaz Sharif", "+923331112234", "Owner"),
        ]
        contact_count = 0
        for vendor_name, cname, cmobile, cdesignation in contacts_data:
            existing = db.query(VendorContactPerson).filter(
                VendorContactPerson.mobile == cmobile
            ).first()
            if not existing:
                contact = VendorContactPerson(
                    vendor_id=vendors[vendor_name].id,
                    name=cname, mobile=cmobile, designation=cdesignation
                )
                db.add(contact)
                contact_count += 1
        db.commit()
        print(f"✓ {contact_count} vendor contacts seeded")

        # ── Vendor Groups (Vendor ↔ Category) ────────────────
        vg_data = [
            ("SolarTech Imports", "Solar Panels"),
            ("SolarTech Imports", "Solar Inverters"),
            ("Green Energy Traders", "Solar Panels"),
            ("Green Energy Traders", "Energy Storage"),
            ("PowerMax Solutions", "Security Systems"),
            ("SunRise EPC", "Mounting Structures"),
            ("SunRise EPC", "Solar Panels"),
        ]
        vg_count = 0
        for vendor_name, cat_name in vg_data:
            existing = db.query(VendorGroup).filter(
                VendorGroup.vendor_id == vendors[vendor_name].id,
                VendorGroup.cat_id == categories[cat_name].id
            ).first()
            if not existing:
                vg = VendorGroup(
                    vendor_id=vendors[vendor_name].id,
                    cat_id=categories[cat_name].id
                )
                db.add(vg)
                vg_count += 1
        db.commit()
        print(f"✓ {vg_count} vendor groups seeded")

        # ── Vendor Brands (Vendor ↔ Brand) ────────────────────
        vb_data = [
            ("SolarTech Imports", "Jinko Solar"),
            ("SolarTech Imports", "Longi Green"),
            ("Green Energy Traders", "Huawei"),
            ("Green Energy Traders", "BYD"),
            ("PowerMax Solutions", "Huawei"),
            ("PowerMax Solutions", "GoodWe"),
            ("SunRise EPC", "Jinko Solar"),
            ("ElectroPak Store", "GoodWe"),
        ]
        vb_count = 0
        for vendor_name, brand_name in vb_data:
            existing = db.query(VendorBrand).filter(
                VendorBrand.vendor_id == vendors[vendor_name].id,
                VendorBrand.brand_id == brands[brand_name].id
            ).first()
            if not existing:
                vb = VendorBrand(
                    vendor_id=vendors[vendor_name].id,
                    brand_id=brands[brand_name].id
                )
                db.add(vb)
                vb_count += 1
        db.commit()
        print(f"✓ {vb_count} vendor brands seeded")

        print("\n✅ Database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
