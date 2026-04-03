# ═══════════════════════════════════════════════════════════════════════
#  DAY 1: Inventory CRUD endpoints (initial scaffold)
#  DAY 2: Switched to sync DB session, added raw-data support
# ═══════════════════════════════════════════════════════════════════════

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schema import Product, Inventory

router = APIRouter(tags=["Inventory"])


# ── DAY 1 START: List products ───────────────────────────────────────
@router.get("/products")
def list_products(db: Session = Depends(get_db)):
    result = db.execute(select(Product).where(Product.is_active == True))
    products = result.scalars().all()
    return [
        {
            "product_id": p.product_id,
            "sku": p.sku,
            "name": p.name,
            "category": p.category,
            "unit_cost": float(p.unit_cost),
            "selling_price": float(p.selling_price),
        }
        for p in products
    ]
# ── DAY 1 END ────────────────────────────────────────────────────────


# ── DAY 1 START: List inventory ──────────────────────────────────────
@router.get("/inventory")
def list_inventory(db: Session = Depends(get_db)):
    stmt = (
        select(Inventory, Product)
        .join(Product, Inventory.product_id == Product.product_id)
    )
    result = db.execute(stmt)
    rows = result.all()
    return [
        {
            "product_id": inv.product_id,
            "product_name": prod.name,
            "sku": prod.sku,
            "quantity_on_hand": inv.quantity_on_hand,
            "reorder_point": inv.reorder_point,
            "reorder_qty": inv.reorder_qty,
            "safety_stock": inv.safety_stock,
            "warehouse_location": inv.warehouse_location,
            "last_restock_date": str(inv.last_restock_date) if inv.last_restock_date else None,
            "needs_reorder": inv.quantity_on_hand <= inv.reorder_point,
        }
        for inv, prod in rows
    ]
# ── DAY 1 END ────────────────────────────────────────────────────────


# ── DAY 2 START: Get single product inventory ────────────────────────
@router.get("/inventory/{product_id}")
def get_inventory(product_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        select(Inventory).where(Inventory.product_id == product_id)
    )
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Inventory record not found")
    return {
        "product_id": inv.product_id,
        "quantity_on_hand": inv.quantity_on_hand,
        "reorder_point": inv.reorder_point,
        "reorder_qty": inv.reorder_qty,
        "safety_stock": inv.safety_stock,
        "needs_reorder": inv.quantity_on_hand <= inv.reorder_point,
    }
# ── DAY 2 END ────────────────────────────────────────────────────────
