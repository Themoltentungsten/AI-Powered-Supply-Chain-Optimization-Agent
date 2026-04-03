# ═══════════════════════════════════════════════════════════════════════
#  Kaggle / retail CSV → local schema (Product, SalesHistory, Inventory)
#
#  Supports common Kaggle layouts:
#  1) Superstore-style: Order Date, Product ID/Name, Category, Sales,
#     Quantity, Discount, Segment (or Region)
#  2) Online Retail (UCI): InvoiceDate, StockCode, Description, Quantity,
#     UnitPrice
#
#  Usage:
#    pip install pandas  # already in project requirements
#    python database/import_kaggle_retail.py --csv "C:\\path\\to\\orders.csv"
#
#  Get data: Kaggle → download dataset → note CSV path (no API key in repo).
#  Examples to search on Kaggle: "superstore sales", "online retail",
#  "sample superstore".
# ═══════════════════════════════════════════════════════════════════════

from __future__ import annotations

import argparse
import re
import sys
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.app.database import Base, engine, SessionLocal
from backend.app.models.schema import (
    Product,
    Supplier,
    ProductSupplier,
    Inventory,
    SalesHistory,
    PurchaseOrderItem,
    PurchaseOrder,
    DemandForecast,
    RiskEvent,
    WeatherData,
)


def _first_mode_str(s: pd.Series) -> str:
    m = s.mode()
    if len(m):
        return str(m.iloc[0])[:50]
    return str(s.iloc[0])[:50] if len(s) else "retail"


def _slug(s: str, max_len: int = 48) -> str:
    s = re.sub(r"\s+", "-", str(s).strip())[:max_len]
    s = re.sub(r"[^a-zA-Z0-9\-]", "", s)
    return s or "sku"


def _norm_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df


def _resolve_common_aliases(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "order_date" not in df.columns:
        if "orderdate" in df.columns:
            df = df.rename(columns={"orderdate": "order_date"})
        else:
            for c in list(df.columns):
                if "order" in c and "date" in c and "ship" not in c:
                    df = df.rename(columns={c: "order_date"})
                    break
    if "product_id" not in df.columns and "productid" in df.columns:
        df = df.rename(columns={"productid": "product_id"})
    return df


def _detect_mode(df: pd.DataFrame) -> str:
    cols = set(df.columns)
    if {"invoicedate", "stockcode", "quantity", "unitprice"} <= cols:
        return "online_retail"
    if "order_date" in cols and "sales" in cols and "quantity" in cols:
        return "superstore"
    preview = ", ".join(sorted(cols)[:40])
    more = " …" if len(cols) > 40 else ""
    raise ValueError(
        "Could not detect CSV format. Need either:\n"
        "  - Superstore-like: order_date + sales + quantity + product_name or product_id\n"
        "  - Online Retail: invoicedate + stockcode + quantity + unitprice\n"
        f"Columns found (normalized): {preview}{more}"
    )


def _prepare_superstore(df: pd.DataFrame) -> pd.DataFrame:
    df = _norm_cols(df)
    df = _resolve_common_aliases(df)
    if "order_date" not in df.columns:
        raise ValueError("Superstore CSV needs an order date column (e.g. Order Date).")

    if "product_id" not in df.columns:
        if "product_name" in df.columns:
            df["product_id"] = df["product_name"].astype(str).str.slice(0, 120)
        else:
            raise ValueError("Superstore CSV needs Product ID or Product Name.")

    if "product_name" not in df.columns:
        df["product_name"] = df["product_id"].astype(str)

    if "category" in df.columns:
        pass
    elif "sub-category" in df.columns:
        df["category"] = df["sub-category"].astype(str)
    else:
        df["category"] = "General"

    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce", dayfirst=False).dt.normalize()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    df["sales"] = pd.to_numeric(df["sales"], errors="coerce").fillna(0.0)
    if "discount" in df.columns:
        df["discount"] = pd.to_numeric(df["discount"], errors="coerce").fillna(0.0)
    else:
        df["discount"] = 0.0
    if "segment" in df.columns:
        df["channel"] = df["segment"].astype(str).str.lower().str.replace(" ", "-")
    elif "region" in df.columns:
        df["channel"] = df["region"].astype(str).str.lower().str.replace(" ", "-")
    else:
        df["channel"] = "retail"

    df = df[(df["quantity"] > 0) & (df["sales"] > 0)]
    df = df.dropna(subset=["order_date", "product_id"])
    return df


def _prepare_online_retail(df: pd.DataFrame) -> pd.DataFrame:
    df = _norm_cols(df)
    df = df.rename(
        columns={
            "invoicedate": "order_date",
            "stockcode": "product_id",
            "description": "product_name",
        }
    )
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce", dayfirst=True).dt.normalize()
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce").fillna(0).astype(int)
    price = pd.to_numeric(df["unitprice"], errors="coerce").fillna(0.0)
    df["sales"] = df["quantity"] * price
    df["discount"] = 0.0
    df["channel"] = df["country"].astype(str).str.lower() if "country" in df.columns else "online"
    df["category"] = "SKU"
    df["product_name"] = df["product_name"].fillna(df["product_id"].astype(str))
    df = df[(df["quantity"] > 0) & (df["sales"] > 0)]
    df = df.dropna(subset=["order_date", "product_id"])
    return df


DEFAULT_SUPPLIERS = [
    {"name": "Global Trade Co.", "email": "orders@globaltrade.com", "phone": "+1-555-0101", "lead": 10, "rel": 0.92, "price": 0.45},
    {"name": "FastShip Logistics", "email": "sales@fastship.com", "phone": "+1-555-0202", "lead": 5, "rel": 0.88, "price": 0.60},
    {"name": "PremiumSource Inc.", "email": "info@premiumsource.com", "phone": "+1-555-0303", "lead": 14, "rel": 0.95, "price": 0.35},
]


def clear_sale_related(session) -> None:
    session.query(PurchaseOrderItem).delete()
    session.query(PurchaseOrder).delete()
    session.query(DemandForecast).delete()
    session.query(SalesHistory).delete()
    session.query(Inventory).delete()
    session.query(ProductSupplier).delete()
    session.query(Product).delete()
    session.query(Supplier).delete()
    session.flush()


def clear_demo_data(session) -> None:
    """Full wipe of demo tables so `seed_data.seed()` can run fresh (includes risks / weather cache)."""
    clear_sale_related(session)
    session.query(RiskEvent).delete()
    session.query(WeatherData).delete()
    session.commit()


def import_csv(csv_path: Path, max_products: int | None = None) -> None:
    print(f"Loading {csv_path} …")
    try:
        df = pd.read_csv(csv_path, encoding="utf-8", low_memory=False)
    except UnicodeDecodeError:
        # Some Kaggle CSVs are encoded in latin-1/cp1252.
        df = pd.read_csv(csv_path, encoding="latin-1", low_memory=False)
    df = _norm_cols(df)
    df = _resolve_common_aliases(df)
    mode = _detect_mode(df)
    print(f"Detected format: {mode}")
    if mode == "superstore":
        df = _prepare_superstore(df)
    else:
        df = _prepare_online_retail(df)

    daily = (
        df.groupby(["order_date", "product_id", "product_name", "category"], as_index=False)
        .agg(
            quantity_sold=("quantity", "sum"),
            revenue=("sales", "sum"),
            promotion_active=("discount", lambda s: bool((pd.to_numeric(s, errors="coerce").fillna(0) > 0).any())),
            channel=("channel", _first_mode_str),
        )
    )

    # Product-level stats for pricing
    product_stats = daily.groupby(["product_id", "product_name", "category"], as_index=False).agg(
        total_qty=("quantity_sold", "sum"),
        total_rev=("revenue", "sum"),
    )
    product_stats["unit_price_est"] = (product_stats["total_rev"] / product_stats["total_qty"].clip(lower=1)).round(2)
    if max_products:
        product_stats = product_stats.nlargest(max_products, "total_qty")

    allowed_ids = set(product_stats["product_id"].astype(str))
    daily = daily[daily["product_id"].astype(str).isin(allowed_ids)]

    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    try:
        clear_sale_related(session)

        print("Inserting suppliers …")
        db_suppliers = []
        for s in DEFAULT_SUPPLIERS:
            sup = Supplier(
                name=s["name"],
                contact_email=s["email"],
                phone=s["phone"],
                avg_lead_time_days=s["lead"],
                reliability_score=s["rel"],
                price_rating=s["price"],
            )
            session.add(sup)
            db_suppliers.append(sup)
        session.flush()

        print(f"Inserting {len(product_stats)} products …")
        pid_map: dict[str, int] = {}
        used_skus: set[str] = set()
        for _, row in product_stats.iterrows():
            ext_id = str(row["product_id"]).strip()
            raw = ext_id.replace(" ", "")[:44]
            sku = raw if raw else _slug(ext_id)
            if len(sku) > 50:
                sku = sku[:50]
            base = sku
            if sku in used_skus:
                sku = f"{base[:40]}-{uuid.uuid4().hex[:6]}"
            used_skus.add(sku)

            price = float(row["unit_price_est"])
            cost = round(price * 0.65, 2)
            p = Product(
                sku=sku[:50],
                name=str(row["product_name"])[:200],
                category=str(row["category"])[:100],
                unit_cost=cost,
                selling_price=price,
                lead_time_days=10,
            )
            session.add(p)
            session.flush()
            pid_map[ext_id] = p.product_id

            if db_suppliers:
                sup = db_suppliers[int(hash(ext_id) % len(db_suppliers))]
                session.add(
                    ProductSupplier(
                        product_id=p.product_id,
                        supplier_id=sup.supplier_id,
                        unit_price=round(cost * 1.05, 2),
                        min_order_qty=10,
                        lead_time_days=sup.avg_lead_time_days,
                    )
                )

        print("Inserting daily sales history …")
        now = datetime.utcnow()
        for _, r in daily.iterrows():
            ext = str(r["product_id"])
            if ext not in pid_map:
                continue
            session.add(
                SalesHistory(
                    product_id=pid_map[ext],
                    sale_date=r["order_date"].date(),
                    quantity_sold=int(r["quantity_sold"]),
                    revenue=round(float(r["revenue"]), 2),
                    channel=str(r["channel"])[:50],
                    promotion_active=bool(r["promotion_active"]),
                    created_at=now,
                )
            )

        print("Deriving inventory from sales stats …")
        for ext_id, internal_id in pid_map.items():
            sub = daily[daily["product_id"].astype(str) == ext_id]
            mean_daily = sub["quantity_sold"].mean()
            mean_daily = float(mean_daily) if pd.notna(mean_daily) else 1.0
            lead = 10
            safety = max(1, int(mean_daily * 7))
            rop = max(1, int(mean_daily * lead + safety))
            eoq = max(10, int(mean_daily * 30))
            qoh = max(int(rop * 0.8), int(mean_daily * 14))

            session.add(
                Inventory(
                    product_id=internal_id,
                    quantity_on_hand=qoh,
                    reorder_point=rop,
                    reorder_qty=eoq,
                    safety_stock=safety,
                    warehouse_location="WH-MAIN",
                    last_restock_date=date.today() - timedelta(days=7),
                )
            )

        session.commit()
        n_sales = session.query(SalesHistory).count()
        print(f"Import complete — {len(pid_map)} products, {n_sales:,} daily sales rows.")
    except Exception as e:
        session.rollback()
        print(f"Import failed: {e}")
        raise
    finally:
        session.close()


def main():
    ap = argparse.ArgumentParser(description="Import Kaggle-style retail CSV into supply_chain DB.")
    ap.add_argument("--csv", type=Path, required=True, help="Path to downloaded CSV file.")
    ap.add_argument(
        "--max-products",
        type=int,
        default=None,
        help="Keep top N products by total quantity (faster demos).",
    )
    args = ap.parse_args()
    if not args.csv.is_file():
        raise SystemExit(f"File not found: {args.csv}")
    import_csv(args.csv, max_products=args.max_products)


if __name__ == "__main__":
    main()
