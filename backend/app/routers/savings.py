# ═══════════════════════════════════════════════════════════════════════
#  DAY 5: Savings report — stockout predictions, overstock holding costs,
#         projected monthly savings from agent-based automation.
# ═══════════════════════════════════════════════════════════════════════

from __future__ import annotations

import math
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schema import (
    Product, Inventory, SalesHistory, PurchaseOrder, DemandForecast, Supplier,
)

router = APIRouter(tags=["Savings Report"])


# ── DAY 5 START: Savings analysis endpoint ────────────────────────────

@router.get("/savings/report")
def savings_report(db: Session = Depends(get_db)):
    cutoff = date.today() - timedelta(days=90)
    products_inv = db.execute(
        select(Product, Inventory)
        .join(Inventory, Inventory.product_id == Product.product_id)
    ).all()

    items = []
    total_overstock = total_stockout = 0.0

    for prod, inv in products_inv:
        total_sold = db.execute(
            select(func.coalesce(func.sum(SalesHistory.quantity_sold), 0))
            .where(SalesHistory.product_id == prod.product_id, SalesHistory.sale_date >= cutoff)
        ).scalar()
        avg_daily = round(float(total_sold) / 90, 2) if total_sold else 0.01

        days_of_stock = round(inv.quantity_on_hand / max(avg_daily, 0.01), 1)
        stockout_date = date.today() + timedelta(days=int(days_of_stock))

        if days_of_stock < 7:
            risk = "critical"
        elif days_of_stock < 14:
            risk = "warning"
        else:
            risk = "ok"

        excess = max(0, inv.quantity_on_hand - inv.reorder_point)
        overstock_cost = round(excess * float(prod.unit_cost) * 0.20 / 365 * 30, 2)

        deficit = max(0, inv.reorder_point - inv.quantity_on_hand)
        stockout_cost = round(deficit * float(prod.selling_price) * 0.5, 2)

        savings = round(overstock_cost + stockout_cost, 2)

        total_overstock += overstock_cost
        total_stockout += stockout_cost

        items.append({
            "product_name": prod.name,
            "sku": prod.sku,
            "category": prod.category,
            "quantity_on_hand": inv.quantity_on_hand,
            "reorder_point": inv.reorder_point,
            "safety_stock": inv.safety_stock,
            "unit_cost": float(prod.unit_cost),
            "selling_price": float(prod.selling_price),
            "avg_daily_demand": avg_daily,
            "days_of_stock": days_of_stock,
            "stockout_date": str(stockout_date),
            "stockout_risk": risk,
            "overstock_cost": overstock_cost,
            "stockout_cost": stockout_cost,
            "potential_savings": savings,
        })

    agent_orders = db.execute(
        select(func.count(PurchaseOrder.po_id), func.coalesce(func.sum(PurchaseOrder.total_amount), 0))
        .where(PurchaseOrder.generated_by == "agent")
    ).one()

    total_pot = round(total_overstock + total_stockout, 2)
    denom = total_overstock + total_stockout
    waste_pct = round(total_overstock / denom * 100, 1) if denom > 0 else 0

    critical_n = sum(1 for i in items if i["stockout_risk"] == "critical")
    warning_n = sum(1 for i in items if i["stockout_risk"] == "warning")
    ok_n = sum(1 for i in items if i["stockout_risk"] == "ok")

    return {
        "products": items,
        "summary": {
            "total_products": len(items),
            "critical_count": critical_n,
            "warning_count": warning_n,
            "ok_count": ok_n,
            "total_overstock_cost": round(total_overstock, 2),
            "total_stockout_cost": round(total_stockout, 2),
            "total_potential_savings": total_pot,
            "agent_orders_count": agent_orders[0],
            "agent_orders_value": round(float(agent_orders[1]), 2),
            "waste_reduction_pct": waste_pct,
        },
    }

# ── DAY 5 END ────────────────────────────────────────────────────────
