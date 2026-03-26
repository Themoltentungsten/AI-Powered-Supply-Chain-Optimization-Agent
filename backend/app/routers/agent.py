# ═══════════════════════════════════════════════════════════════════════
#  DAY 4: Agent orchestration endpoints — run agent per product or scan
#         all products below ROP.  Returns chain-of-thought reasoning,
#         tool call logs, and drafted PO details.
# ═══════════════════════════════════════════════════════════════════════

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schema import Product, Inventory, PurchaseOrder, PurchaseOrderItem, Supplier
from ..services.agent_service import run_agent_for_product, run_agent_scan_all
from ..services.po_generation_service import (
    get_stock_status, calc_avg_daily_demand, calc_rop, calc_eoq,
)

router = APIRouter(tags=["Agent Orchestration"])
logger = logging.getLogger("agent_router")


# ── DAY 4 START: Agent endpoints ──────────────────────────────────────

@router.get("/agent/stock-analysis/{product_id}")
def stock_analysis(product_id: int, db: Session = Depends(get_db)):
    """ROP / EOQ analysis for a single product (no LLM call)."""
    status = get_stock_status(db, product_id)
    if not status:
        raise HTTPException(status_code=404, detail="Product not found")
    return status


@router.post("/agent/run/{product_id}")
def run_agent_single(
    product_id: int,
    location: str = Query(default="New York", description="Weather location for agent context"),
    db: Session = Depends(get_db),
):
    """
    Execute the full ReAct agent loop for one product:
    check inventory → forecast → weather → risk search → supplier selection → PO draft.
    """
    try:
        result = run_agent_for_product(db, product_id, weather_location=location)
        if "error" in result and result["error"]:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Agent run failed")
        raise HTTPException(
            status_code=500,
            detail=f"Agent execution failed: {e}",
        ) from e


@router.post("/agent/scan")
def scan_all_products(
    location: str = Query(default="New York", description="Weather location"),
    db: Session = Depends(get_db),
):
    """
    Scan every product below its ROP and run the agent for each.
    Returns a list of agent decisions + any POs created.
    """
    try:
        results = run_agent_scan_all(db, weather_location=location)
        summary = {
            "total_scanned": len(results),
            "reorders": sum(1 for r in results if r.get("decision") == "REORDER"),
            "no_reorders": sum(1 for r in results if r.get("decision") == "NO_REORDER"),
            "errors": sum(1 for r in results if r.get("error")),
            "results": results,
        }
        return summary
    except Exception as e:
        logger.exception("Scan failed")
        raise HTTPException(status_code=500, detail=f"Scan failed: {e}") from e


@router.get("/agent/po-history")
def agent_po_history(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    """List recent agent-generated POs with reasoning."""
    stmt = (
        select(PurchaseOrder, Supplier)
        .join(Supplier, PurchaseOrder.supplier_id == Supplier.supplier_id)
        .where(PurchaseOrder.generated_by == "agent")
        .order_by(PurchaseOrder.created_at.desc())
        .limit(limit)
    )
    rows = db.execute(stmt).all()
    return [
        {
            "po_id": po.po_id,
            "supplier_name": sup.name,
            "status": po.status,
            "total_amount": float(po.total_amount) if po.total_amount else None,
            "order_date": str(po.order_date),
            "expected_delivery": str(po.expected_delivery) if po.expected_delivery else None,
            "agent_reasoning": po.agent_reasoning,
            "created_at": str(po.created_at),
        }
        for po, sup in rows
    ]

# ── DAY 4 END ────────────────────────────────────────────────────────
