CREATE TABLE purchase_demand_vendors (
    id SERIAL PRIMARY KEY,
    purchase_demand_id INTEGER NOT NULL REFERENCES purchase_demands(id),
    vendor_id INTEGER NOT NULL REFERENCES vendors(id),
    purchase_demand_item_id INTEGER REFERENCES purchase_demand_items(id),
    CONSTRAINT uq_purchase_demand_item_vendor UNIQUE (purchase_demand_id, purchase_demand_item_id, vendor_id)
);
