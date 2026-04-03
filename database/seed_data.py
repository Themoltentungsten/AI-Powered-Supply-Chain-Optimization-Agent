# ═══════════════════════════════════════════════════════════════════════
#  DAY 2: Mock data generation — products, suppliers, inventory,
#         2+ years of daily sales with realistic seasonality, risk events
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
    SalesHistory, RiskEvent, WeatherData,
)

random.seed(42)
np.random.seed(42)

# ── DAY 2 START: Product catalog with seasonal profiles ──────────────

PRODUCTS = [
    {"sku": "WJ-1001", "name": "Winter Jacket",          "category": "Apparel",      "unit_cost": 89.99,  "selling_price": 129.99, "lead_time": 14, "base_demand": 15, "peak_day": 15,  "amplitude": 0.80},
    {"sku": "SS-2001", "name": "Sunscreen SPF50",         "category": "Personal Care","unit_cost": 12.99,  "selling_price": 19.99,  "lead_time": 7,  "base_demand": 25, "peak_day": 196, "amplitude": 0.70},
    {"sku": "UM-3001", "name": "Umbrella Premium",        "category": "Accessories",  "unit_cost": 24.99,  "selling_price": 39.99,  "lead_time": 10, "base_demand": 20, "peak_day": 105, "amplitude": 0.50},
    {"sku": "CB-4001", "name": "Organic Coffee Beans 1kg","category": "Grocery",      "unit_cost": 14.99,  "selling_price": 22.99,  "lead_time": 5,  "base_demand": 40, "peak_day": 350, "amplitude": 0.20},
    {"sku": "VD-5001", "name": "Vitamin D Supplements",   "category": "Health",       "unit_cost": 9.99,   "selling_price": 16.99,  "lead_time": 7,  "base_demand": 30, "peak_day": 1,   "amplitude": 0.50},
    {"sku": "GH-6001", "name": "Garden Hose 50ft",        "category": "Home & Garden","unit_cost": 19.99,  "selling_price": 34.99,  "lead_time": 12, "base_demand": 18, "peak_day": 166, "amplitude": 0.70},
    {"sku": "SP-7001", "name": "School Supplies Pack",    "category": "Stationery",   "unit_cost": 15.99,  "selling_price": 24.99,  "lead_time": 8,  "base_demand": 22, "peak_day": 243, "amplitude": 0.90},
    {"sku": "HG-8001", "name": "Holiday Gift Box",        "category": "Gifts",        "unit_cost": 29.99,  "selling_price": 49.99,  "lead_time": 14, "base_demand": 12, "peak_day": 340, "amplitude": 1.50},
    {"sku": "PB-9001", "name": "Protein Bars (Box/12)",   "category": "Health",       "unit_cost": 18.99,  "selling_price": 29.99,  "lead_time": 6,  "base_demand": 35, "peak_day": 15,  "amplitude": 0.30},
    {"sku": "AM-1010", "name": "Allergy Medicine 30ct",   "category": "Health",       "unit_cost": 11.99,  "selling_price": 19.99,  "lead_time": 7,  "base_demand": 25, "peak_day": 105, "amplitude": 0.60},
]

SUPPLIERS = [
    {"name": "Global Trade Co.",    "email": "orders@globaltrade.com",  "phone": "+1-555-0101", "lead": 10, "reliability": 0.92, "price": 0.45},
    {"name": "FastShip Logistics",  "email": "sales@fastship.com",     "phone": "+1-555-0202", "lead": 5,  "reliability": 0.88, "price": 0.60},
    {"name": "PremiumSource Inc.",  "email": "info@premiumsource.com", "phone": "+1-555-0303", "lead": 14, "reliability": 0.95, "price": 0.35},
    {"name": "BudgetSupply Ltd.",   "email": "bulk@budgetsupply.com",  "phone": "+1-555-0404", "lead": 7,  "reliability": 0.78, "price": 0.75},
    {"name": "EcoWare Partners",    "email": "hello@ecoware.com",      "phone": "+1-555-0505", "lead": 12, "reliability": 0.90, "price": 0.50},
]

RISK_EVENTS = [
    {"type": "port_congestion",        "severity": "high",     "desc": "Major port congestion at Shanghai port causing 2-3 week delays for container shipments from East Asia. Over 50 vessels waiting at anchorage.", "suppliers": "Global Trade Co., PremiumSource Inc.", "region": "East Asia",     "date": "2024-03-15", "source": "news_api"},
    {"type": "weather_disruption",     "severity": "critical", "desc": "Category 4 hurricane approaching Miami. All inbound sea freight and air cargo suspended for southeast US. Expect 10-14 day delays.", "suppliers": "FastShip Logistics",                    "region": "Southeast US",  "date": "2024-08-20", "source": "weather_api"},
    {"type": "supplier_incident",      "severity": "high",     "desc": "Fire at BudgetSupply Ltd. main warehouse. 30% of inventory destroyed. Recovery expected in 6-8 weeks.",                               "suppliers": "BudgetSupply Ltd.",                      "region": "Midwest US",    "date": "2024-11-10", "source": "manual"},
    {"type": "raw_material_shortage",  "severity": "medium",   "desc": "Global cotton shortage due to drought in major producing regions. Prices up 25%. Lead times for apparel items extended by 2 weeks.",   "suppliers": "Global Trade Co., EcoWare Partners",     "region": "Global",        "date": "2024-05-01", "source": "news_api"},
    {"type": "transportation_strike",  "severity": "high",     "desc": "Nationwide truck drivers strike in progress. Ground freight capacity reduced by 60%. Air freight rates surging 3x.",                  "suppliers": "FastShip Logistics, BudgetSupply Ltd.",   "region": "National US",   "date": "2025-02-15", "source": "news_api"},
    {"type": "pandemic_disruption",    "severity": "medium",   "desc": "New COVID variant causing factory shutdowns in manufacturing hubs. 15-20% capacity reduction expected for 4-6 weeks.",                "suppliers": "Global Trade Co., PremiumSource Inc.",    "region": "Southeast Asia","date": "2025-04-10", "source": "news_api"},
    {"type": "customs_delay",          "severity": "medium",   "desc": "New customs inspection requirements at US-Mexico border. Processing times increased from 2 to 8 days. Affects all cross-border shipments.", "suppliers": "BudgetSupply Ltd.",                 "region": "US-Mexico border","date": "2025-06-20","source": "manual"},
    {"type": "warehouse_flooding",     "severity": "high",     "desc": "Flash flooding at EcoWare Partners primary distribution center. Estimated $2M in damaged goods. Alternate routing in progress.",       "suppliers": "EcoWare Partners",                       "region": "Pacific NW",    "date": "2025-09-05", "source": "weather_api"},
    {"type": "quality_recall",         "severity": "critical", "desc": "Mandatory recall on allergy medicine batch AM-1010-2025Q3 due to contamination. 50,000 units affected. FDA investigation pending.",    "suppliers": "PremiumSource Inc.",                      "region": "National US",   "date": "2025-11-15", "source": "manual"},
    {"type": "geopolitical_restriction","severity": "high",    "desc": "New trade tariffs on electronics components from East Asia. 35% additional duty. Affects cost structure for all imported electronics.", "suppliers": "Global Trade Co.",                        "region": "East Asia",     "date": "2026-01-20", "source": "news_api"},
]

# ── DAY 2 END ────────────────────────────────────────────────────────


def generate_daily_sales(product_meta: dict, start: date, end: date):
    """Generate realistic daily sales with seasonality, trend, and noise."""
    base = product_meta["base_demand"]
    peak = product_meta["peak_day"]
    amp = product_meta["amplitude"]
    price = product_meta["selling_price"]
    records = []
    total_days = (end - start).days

    for i in range(total_days + 1):
        d = start + timedelta(days=i)
        day_of_year = d.timetuple().tm_yday

        seasonal = 1 + amp * math.cos(2 * math.pi * (day_of_year - peak) / 365)
        weekend_mult = 1.15 if d.weekday() >= 5 else 1.0
        trend = 1 + 0.0002 * i
        noise = max(0.5, np.random.normal(1.0, 0.18))
        promo = random.random() < 0.05
        promo_mult = 1.5 if promo else 1.0

        qty = max(1, int(base * seasonal * weekend_mult * trend * noise * promo_mult))
        rev = round(qty * price * random.uniform(0.92, 1.0), 2)
        channel = random.choice(["in-store", "in-store", "in-store", "online", "wholesale"])

        records.append({
            "sale_date": d,
            "quantity_sold": qty,
            "revenue": rev,
            "channel": channel,
            "promotion_active": promo,
        })
    return records


def seed():
    print("Creating tables …")
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        if session.query(Product).count() > 0:
            print("Database already seeded — skipping.")
            return

        # ── Products ─────────────────────────────────────────────────
        print("Inserting products …")
        db_products = []
        for p in PRODUCTS:
            prod = Product(
                sku=p["sku"], name=p["name"], category=p["category"],
                unit_cost=p["unit_cost"], selling_price=p["selling_price"],
                lead_time_days=p["lead_time"],
            )
            session.add(prod)
            db_products.append(prod)
        session.flush()

        # ── Suppliers ────────────────────────────────────────────────
        print("Inserting suppliers …")
        db_suppliers = []
        for s in SUPPLIERS:
            sup = Supplier(
                name=s["name"], contact_email=s["email"], phone=s["phone"],
                avg_lead_time_days=s["lead"], reliability_score=s["reliability"],
                price_rating=s["price"],
            )
            session.add(sup)
            db_suppliers.append(sup)
        session.flush()

        # ── Product ↔ Supplier mappings ──────────────────────────────
        for prod in db_products:
            assigned = random.sample(db_suppliers, k=random.randint(2, 4))
            for sup in assigned:
                ps = ProductSupplier(
                    product_id=prod.product_id,
                    supplier_id=sup.supplier_id,
                    unit_price=round(float(prod.unit_cost) * random.uniform(0.85, 1.10), 2),
                    min_order_qty=random.choice([10, 25, 50, 100]),
                    lead_time_days=sup.avg_lead_time_days + random.randint(-2, 3),
                )
                session.add(ps)

        # ── Inventory ────────────────────────────────────────────────
        print("Inserting inventory records …")
        warehouses = ["WH-EAST", "WH-WEST", "WH-CENTRAL"]
        for prod in db_products:
            meta = next(p for p in PRODUCTS if p["sku"] == prod.sku)
            avg_daily = meta["base_demand"]
            lead = meta["lead_time"]
            safety = int(avg_daily * 7)
            rop = int(avg_daily * lead + safety)
            eoq = int(avg_daily * 30)
            qty = random.randint(int(rop * 0.4), int(rop * 2.0))

            inv = Inventory(
                product_id=prod.product_id,
                quantity_on_hand=qty,
                reorder_point=rop,
                reorder_qty=eoq,
                safety_stock=safety,
                warehouse_location=random.choice(warehouses),
                last_restock_date=date.today() - timedelta(days=random.randint(3, 30)),
            )
            session.add(inv)

        # ── Sales history (2 years) ──────────────────────────────────
        print("Generating 2+ years of daily sales history …")
        sales_start = date(2024, 1, 1)
        sales_end = date.today() - timedelta(days=1)

        for prod in db_products:
            meta = next(p for p in PRODUCTS if p["sku"] == prod.sku)
            records = generate_daily_sales(meta, sales_start, sales_end)
            for r in records:
                session.add(SalesHistory(product_id=prod.product_id, **r))

        # ── Risk events ──────────────────────────────────────────────
        print("Inserting risk events …")
        for ev in RISK_EVENTS:
            session.add(RiskEvent(
                event_type=ev["type"],
                severity=ev["severity"],
                description=ev["desc"],
                affected_suppliers=ev["suppliers"],
                affected_region=ev["region"],
                event_date=datetime.strptime(ev["date"], "%Y-%m-%d").date(),
                source=ev["source"],
            ))

        session.commit()
        total_sales = session.query(SalesHistory).count()
        print(f"Seed complete — {len(PRODUCTS)} products, {len(SUPPLIERS)} suppliers, "
              f"{total_sales:,} sales records, {len(RISK_EVENTS)} risk events.")
    except Exception as exc:
        session.rollback()
        print(f"Seed failed: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed()
