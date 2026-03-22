import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy import create_all
from app.db.database import SessionLocal
from app.models.purchase_demand import PurchaseDemand
from app.models.purchase_demand_item import PurchaseDemandItem
from app.models.item import Item

def debug():
    db = SessionLocal()
    try:
        demand = db.query(PurchaseDemand).filter(PurchaseDemand.demand_code == "PD-0025").first()
        if not demand:
            print("PD-0025 not found")
            return
        
        print(f"Demand: {demand.demand_code} (Status: {demand.status})")
        for di in demand.items:
            print(f"  - Item ID: {di.item_id}, Qty: {di.quantity}, Notes: {di.notes}")
            itm = db.query(Item).filter(Item.id == di.item_id).first()
            if itm:
                print(f"    Item Model: {itm.id}, Brand: {itm.brand_id}, SubCat: {itm.scat_id}")
            else:
                print("    !!! ITEM RECORD MISSING IN DATABASE !!!")
    finally:
        db.close()

if __name__ == "__main__":
    debug()
