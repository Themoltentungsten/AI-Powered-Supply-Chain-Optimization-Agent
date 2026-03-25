# ═══════════════════════════════════════════════════════════════════════
#  DAY 1: Sales-history & forecast read endpoints (scaffold)
#  DAY 2: Switched to sync DB session
#  DAY 3: Added POST /forecasts/generate/{product_id} — runs Prophet
# ═══════════════════════════════════════════════════════════════════════

from datetime import date

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schema import SalesHistory, DemandForecast, Product
from ..services.forecasting_service import generate_forecast  # DAY 3

router = APIRouter(tags=["Forecasting"])


# ── DAY 1 START: Get sales history for a product ────────────────────
@router.get("/sales-history/{product_id}")
def get_sales_history(
    product_id: int,
    limit: int = Query(default=1500, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(SalesHistory)
        .where(SalesHistory.product_id == product_id)
        .order_by(SalesHistory.sale_date.desc())
        .limit(limit)
    )
    sales = result.scalars().all()
    if not sales:
        raise HTTPException(status_code=404, detail="No sales history found")
    return [
        {
            "sale_date": str(s.sale_date),
            "quantity_sold": s.quantity_sold,
            "revenue": float(s.revenue) if s.revenue else None,
            "channel": s.channel,
            "promotion_active": s.promotion_active,
        }
        for s in sales
    ]
# ── DAY 1 END ────────────────────────────────────────────────────────


# ── DAY 1 START: Read stored forecasts ──────────────────────────────
@router.get("/forecasts/{product_id}")
def get_forecasts(
    product_id: int,
    db: Session = Depends(get_db),
):
    result = db.execute(
        select(DemandForecast)
        .where(DemandForecast.product_id == product_id)
        .order_by(DemandForecast.forecast_date)
    )
    forecasts = result.scalars().all()
    return [
        {
            "forecast_date": str(f.forecast_date),
            "predicted_demand": float(f.predicted_demand),
            "lower_bound": float(f.lower_bound) if f.lower_bound else None,
            "upper_bound": float(f.upper_bound) if f.upper_bound else None,
            "model_version": f.model_version,
        }
        for f in forecasts
    ]
# ── DAY 1 END ────────────────────────────────────────────────────────


# ── DAY 3 START: Generate demand forecast via Prophet / fallback ─────
@router.post("/forecasts/generate/{product_id}")
def generate_product_forecast(
    product_id: int,
    periods: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
):
    prod = db.execute(
        select(Product).where(Product.product_id == product_id)
    ).scalar_one_or_none()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")

    rows = db.execute(
        select(SalesHistory)
        .where(SalesHistory.product_id == product_id)
        .order_by(SalesHistory.sale_date)
    ).scalars().all()

    if len(rows) < 30:
        raise HTTPException(status_code=400, detail="Not enough sales history (need ≥ 30 days)")

    sales_df = pd.DataFrame([
        {
            "sale_date": str(r.sale_date),
            "quantity_sold": r.quantity_sold,
            "promotion_active": r.promotion_active,
        }
        for r in rows
    ])

    forecast_df, model_version = generate_forecast(sales_df, periods)

    db.execute(
        delete(DemandForecast).where(DemandForecast.product_id == product_id)
    )

    for _, row in forecast_df.iterrows():
        db.add(DemandForecast(
            product_id=product_id,
            forecast_date=row["ds"].date() if hasattr(row["ds"], "date") else row["ds"],
            predicted_demand=round(float(row["yhat"]), 2),
            lower_bound=round(float(row["yhat_lower"]), 2),
            upper_bound=round(float(row["yhat_upper"]), 2),
            model_version=model_version,
        ))
    db.commit()

    return {
        "product_id": product_id,
        "product_name": prod.name,
        "periods": periods,
        "model_used": model_version,
        "forecast": [
            {
                "date": str(row["ds"].date() if hasattr(row["ds"], "date") else row["ds"]),
                "predicted": round(float(row["yhat"]), 2),
                "lower": round(float(row["yhat_lower"]), 2),
                "upper": round(float(row["yhat_upper"]), 2),
            }
            for _, row in forecast_df.iterrows()
        ],
    }
# ── DAY 3 END ────────────────────────────────────────────────────────
