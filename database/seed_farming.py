# ═══════════════════════════════════════════════════════════════════════
#  DAY 4: Farming / Crops seed dataset
#  Mixed stock levels: some ABOVE ROP, some BELOW ROP, some BELOW safety
#  Includes crop-specific risk alerts (drought, pests, floods, etc.)
# ═══════════════════════════════════════════════════════════════════════

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import math
import random
from datetime import date, datetime, timedelta

import numpy as np

from backend.app.database import engine, Base, SessionLocal
from backend.app.models.schema import (
    Product, Supplier, ProductSupplier, Inventory,
    SalesHistory, RiskEvent, DataSource,
)

random.seed(99)
np.random.seed(99)

# ── Crop products with seasonal profiles ──────────────────────────────
# stock_zone: "above" = comfortably above ROP
#             "below_rop" = between safety stock and ROP
#             "critical"  = below safety stock

CROPS = [
    {"sku": "CR-RICE",   "name": "Basmati Rice (50kg)",     "category": "Grains",      "unit_cost": 45.00, "selling_price": 72.00,  "lead_time": 10, "base_demand": 25, "peak_day": 300, "amplitude": 0.40, "stock_zone": "below_rop"},
    {"sku": "CR-WHEAT",  "name": "Wheat Grain (50kg)",      "category": "Grains",      "unit_cost": 32.00, "selling_price": 52.00,  "lead_time": 8,  "base_demand": 30, "peak_day": 90,  "amplitude": 0.35, "stock_zone": "above"},
    {"sku": "CR-CORN",   "name": "Corn / Maize (50kg)",     "category": "Grains",      "unit_cost": 28.00, "selling_price": 45.00,  "lead_time": 7,  "base_demand": 20, "peak_day": 180, "amplitude": 0.50, "stock_zone": "critical"},
    {"sku": "CR-TOMATO", "name": "Fresh Tomatoes (20kg)",   "category": "Vegetables",  "unit_cost": 15.00, "selling_price": 28.00,  "lead_time": 3,  "base_demand": 40, "peak_day": 200, "amplitude": 0.60, "stock_zone": "below_rop"},
    {"sku": "CR-POTATO", "name": "Potatoes (50kg)",         "category": "Vegetables",  "unit_cost": 18.00, "selling_price": 30.00,  "lead_time": 5,  "base_demand": 35, "peak_day": 30,  "amplitude": 0.25, "stock_zone": "above"},
    {"sku": "CR-ONION",  "name": "Red Onions (25kg)",       "category": "Vegetables",  "unit_cost": 12.00, "selling_price": 22.00,  "lead_time": 4,  "base_demand": 45, "peak_day": 330, "amplitude": 0.55, "stock_zone": "critical"},
    {"sku": "CR-MANGO",  "name": "Alphonso Mangoes (10kg)", "category": "Fruits",      "unit_cost": 35.00, "selling_price": 65.00,  "lead_time": 2,  "base_demand": 15, "peak_day": 135, "amplitude": 1.20, "stock_zone": "below_rop"},
    {"sku": "CR-COTTON", "name": "Raw Cotton Bale",         "category": "Cash Crops",  "unit_cost": 120.00,"selling_price": 185.00, "lead_time": 14, "base_demand": 8,  "peak_day": 270, "amplitude": 0.60, "stock_zone": "above"},
    {"sku": "CR-SUGAR",  "name": "Sugarcane Extract (50L)", "category": "Cash Crops",  "unit_cost": 55.00, "selling_price": 88.00,  "lead_time": 10, "base_demand": 12, "peak_day": 320, "amplitude": 0.45, "stock_zone": "critical"},
    {"sku": "CR-SOY",    "name": "Soybeans (50kg)",         "category": "Oilseeds",    "unit_cost": 38.00, "selling_price": 60.00,  "lead_time": 7,  "base_demand": 18, "peak_day": 240, "amplitude": 0.40, "stock_zone": "below_rop"},
    {"sku": "CR-TEA",    "name": "Green Tea Leaves (5kg)",  "category": "Beverages",   "unit_cost": 25.00, "selling_price": 48.00,  "lead_time": 6,  "base_demand": 22, "peak_day": 60,  "amplitude": 0.30, "stock_zone": "above"},
    {"sku": "CR-CHILI",  "name": "Dried Red Chili (10kg)",  "category": "Spices",      "unit_cost": 20.00, "selling_price": 38.00,  "lead_time": 5,  "base_demand": 28, "peak_day": 150, "amplitude": 0.55, "stock_zone": "below_rop"},
    {"sku": "CR-COFFEE", "name": "Arabica Coffee (10kg)",   "category": "Beverages",   "unit_cost": 65.00, "selling_price": 110.00, "lead_time": 12, "base_demand": 10, "peak_day": 350, "amplitude": 0.35, "stock_zone": "critical"},
    {"sku": "CR-BANANA", "name": "Bananas (25kg bunch)",    "category": "Fruits",      "unit_cost": 8.00,  "selling_price": 16.00,  "lead_time": 2,  "base_demand": 50, "peak_day": 160, "amplitude": 0.30, "stock_zone": "above"},
    {"sku": "CR-PEPPER", "name": "Black Pepper (5kg)",      "category": "Spices",      "unit_cost": 42.00, "selling_price": 75.00,  "lead_time": 8,  "base_demand": 14, "peak_day": 280, "amplitude": 0.50, "stock_zone": "below_rop"},
]

AGRI_SUPPLIERS = [
    {"name": "FarmFresh Co-op",         "email": "orders@farmfresh.coop",   "phone": "+91-9876-001001", "lead": 5,  "reliability": 0.93, "price": 0.40},
    {"name": "AgriDirect Wholesale",    "email": "sales@agridirect.com",    "phone": "+91-9876-002002", "lead": 7,  "reliability": 0.88, "price": 0.55},
    {"name": "Green Harvest Traders",   "email": "info@greenharv.com",      "phone": "+91-9876-003003", "lead": 10, "reliability": 0.95, "price": 0.35},
    {"name": "QuickCrop Logistics",     "email": "dispatch@quickcrop.in",   "phone": "+91-9876-004004", "lead": 3,  "reliability": 0.82, "price": 0.70},
    {"name": "Organic Valley Farms",    "email": "hello@organicvalley.com", "phone": "+91-9876-005005", "lead": 8,  "reliability": 0.91, "price": 0.45},
]

AGRI_RISKS = [
    {"type": "drought",               "severity": "critical", "desc": "Severe drought in Maharashtra and Karnataka. Groundwater levels critically low. Sugarcane and cotton yields expected to drop 40%. Irrigation costs surging.", "suppliers": "FarmFresh Co-op, Green Harvest Traders", "region": "Western India", "date": "2025-04-10"},
    {"type": "pest_outbreak",          "severity": "high",     "desc": "Locust swarm detected in Rajasthan moving towards Gujarat. Crops at risk: wheat, corn, soybeans. Government issuing pesticide advisories.", "suppliers": "AgriDirect Wholesale", "region": "North-West India", "date": "2025-05-20"},
    {"type": "monsoon_flooding",       "severity": "critical", "desc": "Unusually heavy monsoon causing widespread flooding in Bihar and UP. Rice paddy fields submerged. 30% crop loss estimated. Road transport disrupted for 2 weeks.", "suppliers": "FarmFresh Co-op, QuickCrop Logistics", "region": "North India", "date": "2025-07-15"},
    {"type": "cold_wave",              "severity": "high",     "desc": "Unexpected cold wave in Punjab. Potato and wheat crops showing frost damage. Market prices expected to rise 20-30% in next 2 months.", "suppliers": "AgriDirect Wholesale, FarmFresh Co-op", "region": "Punjab", "date": "2025-12-20"},
    {"type": "transportation_strike",  "severity": "high",     "desc": "Truck drivers strike across South India. Perishable goods (tomatoes, bananas, mangoes) cannot reach markets. 60% reduction in fruit/vegetable supply.", "suppliers": "QuickCrop Logistics, Organic Valley Farms", "region": "South India", "date": "2025-08-05"},
    {"type": "export_ban",             "severity": "medium",   "desc": "Government imposes temporary export ban on rice and wheat to stabilize domestic prices. Warehouses overstocked with export-grade grain.", "suppliers": "Green Harvest Traders", "region": "National", "date": "2025-09-01"},
    {"type": "quality_contamination",  "severity": "critical", "desc": "Aflatoxin contamination detected in chili and pepper shipments from Andhra Pradesh. 25,000 kg quarantined. FSSAI recall issued.", "suppliers": "AgriDirect Wholesale, Organic Valley Farms", "region": "Andhra Pradesh", "date": "2025-10-15"},
    {"type": "heatwave",              "severity": "high",     "desc": "Prolonged heatwave (48°C) in Madhya Pradesh. Coffee and tea plantation yields dropping. Workers unable to harvest. Supply expected to fall 35%.", "suppliers": "Green Harvest Traders", "region": "Central India", "date": "2026-03-10"},
    {"type": "warehouse_pest",         "severity": "medium",   "desc": "Grain weevil infestation discovered at QuickCrop Logistics warehouse. 5,000 kg of stored wheat and rice affected. Fumigation in progress.", "suppliers": "QuickCrop Logistics", "region": "Delhi NCR", "date": "2026-01-25"},
    {"type": "currency_volatility",    "severity": "medium",   "desc": "INR depreciation against USD increasing import costs for fertilizers and pesticides. Farming input costs up 15%. Downstream crop prices rising.", "suppliers": "All suppliers", "region": "National", "date": "2026-02-10"},
]


def generate_crop_sales(crop: dict, start: date, end: date):
    base = crop["base_demand"]
    peak = crop["peak_day"]
    amp = crop["amplitude"]
    price = crop["selling_price"]
    records = []
    total_days = (end - start).days

    for i in range(total_days + 1):
        d = start + timedelta(days=i)
        day_of_year = d.timetuple().tm_yday
        seasonal = 1 + amp * math.cos(2 * math.pi * (day_of_year - peak) / 365)
        weekend_mult = 0.85 if d.weekday() >= 5 else 1.0  # farms sell less on weekends
        trend = 1 + 0.0001 * i
        noise = max(0.4, np.random.normal(1.0, 0.22))
        promo = random.random() < 0.04
        promo_mult = 1.4 if promo else 1.0

        qty = max(1, int(base * seasonal * weekend_mult * trend * noise * promo_mult))
        rev = round(qty * price * random.uniform(0.90, 1.0), 2)
        channel = random.choice(["mandi", "mandi", "mandi", "online", "wholesale", "export"])

        records.append({
            "sale_date": d,
            "quantity_sold": qty,
            "revenue": rev,
            "channel": channel,
            "promotion_active": promo,
        })
    return records


def seed_farming():
    print("Creating tables …")
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        # ── Clear existing data ───────────────────────────────────────
        from backend.app.models.schema import (
            PurchaseOrderItem, PurchaseOrder, DemandForecast,
            WeatherData, DataSource,
        )
        for model in [PurchaseOrderItem, PurchaseOrder, DemandForecast,
                      SalesHistory, Inventory, ProductSupplier,
                      RiskEvent, WeatherData, DataSource, Supplier, Product]:
            session.query(model).delete()
        session.commit()
        print("Cleared old data.")

        # ── Products (crops) ──────────────────────────────────────────
        print("Inserting 15 crop products …")
        db_products = []
        for c in CROPS:
            prod = Product(
                sku=c["sku"], name=c["name"], category=c["category"],
                unit_cost=c["unit_cost"], selling_price=c["selling_price"],
                lead_time_days=c["lead_time"],
            )
            session.add(prod)
            db_products.append(prod)
        session.flush()

        # ── Suppliers ─────────────────────────────────────────────────
        print("Inserting agricultural suppliers …")
        db_suppliers = []
        for s in AGRI_SUPPLIERS:
            sup = Supplier(
                name=s["name"], contact_email=s["email"], phone=s["phone"],
                avg_lead_time_days=s["lead"], reliability_score=s["reliability"],
                price_rating=s["price"],
            )
            session.add(sup)
            db_suppliers.append(sup)
        session.flush()

        # ── Product ↔ Supplier links ─────────────────────────────────
        for prod in db_products:
            assigned = random.sample(db_suppliers, k=random.randint(2, 4))
            for sup in assigned:
                ps = ProductSupplier(
                    product_id=prod.product_id,
                    supplier_id=sup.supplier_id,
                    unit_price=round(float(prod.unit_cost) * random.uniform(0.88, 1.08), 2),
                    min_order_qty=random.choice([10, 20, 50, 100]),
                    lead_time_days=sup.avg_lead_time_days + random.randint(-1, 3),
                )
                session.add(ps)

        # ── Inventory with MIXED stock levels ─────────────────────────
        print("Inserting inventory with mixed stock levels …")
        warehouses = ["WH-NORTH", "WH-SOUTH", "WH-WEST", "WH-CENTRAL"]
        for prod in db_products:
            meta = next(c for c in CROPS if c["sku"] == prod.sku)
            avg_daily = meta["base_demand"]
            lead = meta["lead_time"]
            safety = int(avg_daily * 7)
            rop = int(avg_daily * lead + safety)
            eoq = int(avg_daily * 30)

            zone = meta["stock_zone"]
            if zone == "above":
                qty = random.randint(int(rop * 1.2), int(rop * 2.5))
            elif zone == "below_rop":
                qty = random.randint(safety + 5, rop - 1)
            else:  # critical — below safety stock
                qty = random.randint(3, max(4, safety - 5))

            inv = Inventory(
                product_id=prod.product_id,
                quantity_on_hand=qty,
                reorder_point=rop,
                reorder_qty=eoq,
                safety_stock=safety,
                warehouse_location=random.choice(warehouses),
                last_restock_date=date.today() - timedelta(days=random.randint(5, 45)),
            )
            session.add(inv)

        # ── Sales history (2 years) ───────────────────────────────────
        print("Generating 2 years of daily crop sales …")
        sales_start = date(2024, 1, 1)
        sales_end = date.today() - timedelta(days=1)

        for prod in db_products:
            meta = next(c for c in CROPS if c["sku"] == prod.sku)
            records = generate_crop_sales(meta, sales_start, sales_end)
            for r in records:
                session.add(SalesHistory(product_id=prod.product_id, **r))

        # ── Risk events (agriculture-specific) ─────────────────────────
        print("Inserting farming risk events …")
        for ev in AGRI_RISKS:
            session.add(RiskEvent(
                event_type=ev["type"],
                severity=ev["severity"],
                description=ev["desc"],
                affected_suppliers=ev["suppliers"],
                affected_region=ev["region"],
                event_date=datetime.strptime(ev["date"], "%Y-%m-%d").date(),
                source="agri_intel",
            ))

        # ── DataSource record ──────────────────────────────────────────
        ds = DataSource(
            name="Farming Crops Dataset",
            source_type="synthetic_farming",
            product_count=len(CROPS),
            sales_count=0,
            is_active=True,
        )
        session.add(ds)

        session.commit()
        total_sales = session.query(SalesHistory).count()
        ds.sales_count = total_sales
        session.commit()

        above = sum(1 for c in CROPS if c["stock_zone"] == "above")
        below = sum(1 for c in CROPS if c["stock_zone"] == "below_rop")
        crit  = sum(1 for c in CROPS if c["stock_zone"] == "critical")

        print(f"\nFarming seed complete!")
        print(f"  {len(CROPS)} crops, {len(AGRI_SUPPLIERS)} suppliers, "
              f"{total_sales:,} sales rows, {len(AGRI_RISKS)} risk events")
        print(f"  Stock levels: {above} above ROP | {below} below ROP | {crit} CRITICAL (below safety)")

    except Exception as exc:
        session.rollback()
        print(f"Seed failed: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_farming()
