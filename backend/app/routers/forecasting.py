from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_db
from ..models.schema import SalesHistory, DemandForecast, Product

router = APIRouter(tags=["Forecasting"])


@router.get("/sales-history/{product_id}")
async def get_sales_history(
    product_id: int,
    limit: int = Query(default=365, ge=1, le=3650),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
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


@router.get("/forecasts/{product_id}")
async def get_forecasts(
    product_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
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
