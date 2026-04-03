# ═══════════════════════════════════════════════════════════════════════
#  DAY 3: Demand forecasting — Prophet (primary) with numpy fallback
# ═══════════════════════════════════════════════════════════════════════

import math
from datetime import date, timedelta

import numpy as np
import pandas as pd

# ── DAY 3 START: Prophet import with graceful fallback ───────────────
try:
    from prophet import Prophet
    PROPHET_AVAILABLE = True
except ImportError:
    PROPHET_AVAILABLE = False
# ── DAY 3 END (import) ──────────────────────────────────────────────


# ── DAY 3 START: Prophet-based demand forecasting ────────────────────

def forecast_with_prophet(
    sales_df: pd.DataFrame,
    periods: int = 30,
) -> pd.DataFrame:
    """
    Train Prophet on historical sales and return `periods` days of forecast.
    Expects sales_df with columns: sale_date, quantity_sold.
    Returns DataFrame with: ds, yhat, yhat_lower, yhat_upper.
    """
    df = sales_df.rename(columns={"sale_date": "ds", "quantity_sold": "y"})
    df["ds"] = pd.to_datetime(df["ds"])

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        daily_seasonality=False,
        changepoint_prior_scale=0.05,
        seasonality_mode="multiplicative",
    )

    if "promotion_active" in sales_df.columns:
        df["promo"] = sales_df["promotion_active"].astype(int)
        model.add_regressor("promo")

    model.fit(df)

    future = model.make_future_dataframe(periods=periods)
    if "promo" in df.columns:
        future["promo"] = 0

    forecast = model.predict(future)
    result = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods).copy()
    result["yhat"] = result["yhat"].clip(lower=0)
    result["yhat_lower"] = result["yhat_lower"].clip(lower=0)
    result["yhat_upper"] = result["yhat_upper"].clip(lower=0)
    return result

# ── DAY 3 END (Prophet) ─────────────────────────────────────────────


# ── DAY 3 START: Numpy seasonal fallback when Prophet unavailable ────

def forecast_with_fallback(
    sales_df: pd.DataFrame,
    periods: int = 30,
) -> pd.DataFrame:
    """
    Seasonal-naive forecast: use last year same-period averages + trend.
    Works without Prophet; gives reasonable seasonal graphs.
    """
    df = sales_df.copy()
    df["sale_date"] = pd.to_datetime(df["sale_date"])
    df = df.sort_values("sale_date")
    df["day_of_year"] = df["sale_date"].dt.dayofyear

    daily_avg = df.groupby("day_of_year")["quantity_sold"].agg(["mean", "std"]).reset_index()
    daily_avg.columns = ["day_of_year", "avg", "std"]
    daily_avg["std"] = daily_avg["std"].fillna(daily_avg["avg"] * 0.15)

    n = len(df)
    if n > 60:
        recent = df.tail(60)["quantity_sold"]
        trend_per_day = np.polyfit(range(len(recent)), recent.values, 1)[0]
    else:
        trend_per_day = 0

    last_date = df["sale_date"].max()
    rows = []
    for i in range(1, periods + 1):
        d = last_date + timedelta(days=i)
        doy = d.timetuple().tm_yday
        match = daily_avg[daily_avg["day_of_year"] == doy]
        if not match.empty:
            avg_val = match["avg"].values[0]
            std_val = match["std"].values[0]
        else:
            avg_val = df["quantity_sold"].mean()
            std_val = df["quantity_sold"].std() * 0.15

        yhat = max(0, avg_val + trend_per_day * i)
        rows.append({
            "ds": d,
            "yhat": round(yhat, 2),
            "yhat_lower": round(max(0, yhat - 1.96 * std_val), 2),
            "yhat_upper": round(yhat + 1.96 * std_val, 2),
        })

    return pd.DataFrame(rows)

# ── DAY 3 END (fallback) ────────────────────────────────────────────


# ── DAY 3 START: Unified forecast entry point ────────────────────────

def generate_forecast(sales_df: pd.DataFrame, periods: int = 30) -> tuple[pd.DataFrame, str]:
    """
    Returns (forecast_df, model_version).
    Uses Prophet when available, falls back to seasonal-naive.
    """
    if PROPHET_AVAILABLE and len(sales_df) >= 60:
        return forecast_with_prophet(sales_df, periods), "prophet_v1"
    return forecast_with_fallback(sales_df, periods), "seasonal_naive_v1"

# ── DAY 3 END (unified) ─────────────────────────────────────────────
