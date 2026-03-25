# ═══════════════════════════════════════════════════════════════════════
#  DAY 1: Purchase-order read endpoints (scaffold)
#  DAY 2: Switched to sync DB session
# ═══════════════════════════════════════════════════════════════════════

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schema import PurchaseOrder, PurchaseOrderItem, Supplier

router = APIRouter(tags=["Purchase Orders"])


# ── DAY 1 START: List purchase orders ────────────────────────────────
@router.get("/purchase-orders")
def list_purchase_orders(db: Session = Depends(get_db)):
    stmt = (
        select(PurchaseOrder, Supplier)
        .join(Supplier, PurchaseOrder.supplier_id == Supplier.supplier_id)
        .order_by(PurchaseOrder.created_at.desc())
    )
    result = db.execute(stmt)
    rows = result.all()
    return [
        {
            "po_id": po.po_id,
            "supplier_name": sup.name,
            "status": po.status,
            "total_amount": float(po.total_amount) if po.total_amount else None,
            "order_date": str(po.order_date),
            "expected_delivery": str(po.expected_delivery) if po.expected_delivery else None,
            "generated_by": po.generated_by,
            "agent_reasoning": po.agent_reasoning,
        }
        for po, sup in rows
    ]
# ── DAY 1 END ────────────────────────────────────────────────────────


# ── DAY 1 START: Get PO detail ──────────────────────────────────────
@router.get("/purchase-orders/{po_id}")
def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        select(PurchaseOrder).where(PurchaseOrder.po_id == po_id)
    )
    po = result.scalar_one_or_none()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    items_result = db.execute(
        select(PurchaseOrderItem).where(PurchaseOrderItem.po_id == po_id)
    )
    items = items_result.scalars().all()

    return {
        "po_id": po.po_id,
        "supplier_id": po.supplier_id,
        "status": po.status,
        "total_amount": float(po.total_amount) if po.total_amount else None,
        "order_date": str(po.order_date),
        "expected_delivery": str(po.expected_delivery) if po.expected_delivery else None,
        "generated_by": po.generated_by,
        "agent_reasoning": po.agent_reasoning,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
            }
            for item in items
        ],
    }
# ── DAY 1 END ────────────────────────────────────────────────────────
