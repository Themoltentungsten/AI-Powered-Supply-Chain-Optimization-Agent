# ═══════════════════════════════════════════════════════════════════════
#  DAY 4: Purchase Order generation — ROP / EOQ calculations,
#         supplier selection, and PO drafting logic.
# ═══════════════════════════════════════════════════════════════════════

from __future__ import annotations

import math
from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..models.schema import (
    Product, Supplier, ProductSupplier, Inventory,
    SalesHistory, DemandForecast, PurchaseOrder, PurchaseOrderItem,
)

# ── DAY 4 START: ROP / EOQ helpers ───────────────────────────────────

def calc_avg_daily_demand(db: Session, product_id: int, lookback_days: int = 90) -> float:
    cutoff = date.today() - timedelta(days=lookback_days)
    total = db.execute(
        select(func.coalesce(func.sum(SalesHistory.quantity_sold), 0))
        .where(SalesHistory.product_id == product_id, SalesHistory.sale_date >= cutoff)
    ).scalar()
    return round(float(total) / max(lookback_days, 1), 2)


def calc_rop(avg_daily: float, lead_time_days: int, safety_stock: int) -> int:
    return max(1, math.ceil(avg_daily * lead_time_days + safety_stock))


def calc_eoq(annual_demand: float, ordering_cost: float = 50.0, holding_pct: float = 0.20, unit_cost: float = 1.0) -> int:
    holding = unit_cost * holding_pct
    if holding <= 0 or annual_demand <= 0:
        return 50
    return max(10, int(math.sqrt(2 * annual_demand * ordering_cost / holding)))

# ── DAY 4 END ────────────────────────────────────────────────────────


# ── DAY 4 START: Supplier scoring & selection ─────────────────────────

def score_supplier(sup: Supplier, ps: ProductSupplier) -> dict:
    price_norm = max(0, 1 - float(sup.price_rating or 0.5))
    reliability = float(sup.reliability_score or 0.5)
    lead_penalty = max(0, 1 - (sup.avg_lead_time_days or 7) / 30)
    score = round(0.35 * reliability + 0.35 * price_norm + 0.30 * lead_penalty, 3)
    return {
        "supplier_id": sup.supplier_id,
        "supplier_name": sup.name,
        "unit_price": float(ps.unit_price),
        "lead_time": ps.lead_time_days or sup.avg_lead_time_days,
        "reliability": reliability,
        "price_rating": float(sup.price_rating or 0.5),
        "composite_score": score,
    }


def select_best_supplier(db: Session, product_id: int) -> dict | None:
    rows = db.execute(
        select(Supplier, ProductSupplier)
        .join(ProductSupplier, ProductSupplier.supplier_id == Supplier.supplier_id)
        .where(ProductSupplier.product_id == product_id, Supplier.is_active == True)
    ).all()
    if not rows:
        return None
    scored = [score_supplier(sup, ps) for sup, ps in rows]
    return max(scored, key=lambda s: s["composite_score"])

# ── DAY 4 END ────────────────────────────────────────────────────────


# ── DAY 4 START: PO creation ─────────────────────────────────────────

def get_stock_status(db: Session, product_id: int) -> dict:
    prod = db.get(Product, product_id)
    inv = db.execute(
        select(Inventory).where(Inventory.product_id == product_id)
    ).scalar_one_or_none()
    if not prod or not inv:
        return {}

    avg_daily = calc_avg_daily_demand(db, product_id)
    annual_demand = avg_daily * 365
    rop = calc_rop(avg_daily, prod.lead_time_days, inv.safety_stock)
    eoq = calc_eoq(annual_demand, unit_cost=float(prod.unit_cost))

    forecast_30 = db.execute(
        select(func.coalesce(func.sum(DemandForecast.predicted_demand), 0))
        .where(DemandForecast.product_id == product_id)
    ).scalar()

    needs_reorder = inv.quantity_on_hand <= rop

    return {
        "product_id": product_id,
        "product_name": prod.name,
        "sku": prod.sku,
        "quantity_on_hand": inv.quantity_on_hand,
        "safety_stock": inv.safety_stock,
        "lead_time_days": prod.lead_time_days,
        "avg_daily_demand": avg_daily,
        "reorder_point_calc": rop,
        "eoq_calc": eoq,
        "forecast_demand_30d": round(float(forecast_30), 1),
        "needs_reorder": needs_reorder,
        "unit_cost": float(prod.unit_cost),
    }


def draft_purchase_order(
    db: Session,
    product_id: int,
    quantity: int,
    supplier_info: dict,
    reasoning: str = "",
) -> dict:
    unit_price = supplier_info["unit_price"]
    lead_time = supplier_info["lead_time"]

    po = PurchaseOrder(
        supplier_id=supplier_info["supplier_id"],
        status="draft",
        total_amount=round(quantity * unit_price, 2),
        order_date=date.today(),
        expected_delivery=date.today() + timedelta(days=lead_time),
        generated_by="agent",
        agent_reasoning=reasoning,
    )
    db.add(po)
    db.flush()

    item = PurchaseOrderItem(
        po_id=po.po_id,
        product_id=product_id,
        quantity=quantity,
        unit_price=unit_price,
    )
    db.add(item)
    db.commit()
    db.refresh(po)

    return {
        "po_id": po.po_id,
        "supplier": supplier_info["supplier_name"],
        "quantity": quantity,
        "unit_price": unit_price,
        "total": round(quantity * unit_price, 2),
        "expected_delivery": str(po.expected_delivery),
        "status": po.status,
        "reasoning": reasoning,
    }

# ── DAY 4 END ────────────────────────────────────────────────────────
