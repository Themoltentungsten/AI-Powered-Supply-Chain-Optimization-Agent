from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models.schema import PurchaseOrder, PurchaseOrderItem, Supplier

router = APIRouter(tags=["Purchase Orders"])


@router.get("/purchase-orders")
async def list_purchase_orders(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(PurchaseOrder, Supplier)
        .join(Supplier, PurchaseOrder.supplier_id == Supplier.supplier_id)
        .order_by(PurchaseOrder.created_at.desc())
    )
    result = await db.execute(stmt)
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


@router.get("/purchase-orders/{po_id}")
async def get_purchase_order(po_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(PurchaseOrder).where(PurchaseOrder.po_id == po_id)
    )
    po = result.scalar_one_or_none()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    items_result = await db.execute(
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
