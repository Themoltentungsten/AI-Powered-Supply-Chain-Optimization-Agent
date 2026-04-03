# ═══════════════════════════════════════════════════════════════════════
#  DAY 4: LangChain ReAct agent — monitors stock, interprets forecasts,
#         fetches live weather, searches risk intelligence, and
#         autonomously drafts POs.
#  Uses OpenAI GPT as the LLM backbone with chain-of-thought reasoning.
# ═══════════════════════════════════════════════════════════════════════

from __future__ import annotations

import json
import logging
from datetime import date

import pandas as pd
from sqlalchemy import select, func, delete
from sqlalchemy.orm import Session

from ..config import get_settings
from ..models.schema import (
    Product, Inventory, SalesHistory, DemandForecast, RiskEvent,
    PurchaseOrder, PurchaseOrderItem,
)
from .po_generation_service import (
    get_stock_status, select_best_supplier, draft_purchase_order,
    calc_avg_daily_demand, calc_rop, calc_eoq,
)
from .risk_rag_service import search_risks
from .forecasting_service import generate_forecast
from .weather_service import fetch_current_weather

logger = logging.getLogger("agent")

# ── DAY 4 START: LangChain tool definitions ──────────────────────────

_TOOL_LOG: list[dict] = []


def _log(tool: str, inp: str, out: str):
    _TOOL_LOG.append({"tool": tool, "input": inp, "output": out[:500]})


def tool_check_inventory(db: Session, product_id: int) -> str:
    status = get_stock_status(db, product_id)
    if not status:
        return json.dumps({"error": f"Product {product_id} not found"})
    _log("check_inventory", str(product_id), json.dumps(status))
    return json.dumps(status)


def _auto_generate_forecast(db: Session, product_id: int, periods: int = 30):
    """Generate forecast on-the-fly if none exists in DB."""
    rows = db.execute(
        select(SalesHistory)
        .where(SalesHistory.product_id == product_id)
        .order_by(SalesHistory.sale_date)
    ).scalars().all()

    if len(rows) < 30:
        return None

    sales_df = pd.DataFrame([
        {
            "sale_date": str(r.sale_date),
            "quantity_sold": r.quantity_sold,
            "promotion_active": r.promotion_active,
        }
        for r in rows
    ])

    try:
        forecast_df, model_version = generate_forecast(sales_df, periods)
    except Exception as exc:
        logger.warning(f"Auto-forecast failed: {exc}")
        return None

    db.execute(delete(DemandForecast).where(DemandForecast.product_id == product_id))
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
    return model_version


def tool_get_forecast(db: Session, product_id: int) -> str:
    rows = db.execute(
        select(DemandForecast)
        .where(DemandForecast.product_id == product_id)
        .order_by(DemandForecast.forecast_date)
    ).scalars().all()

    if not rows:
        logger.info(f"No forecast for product {product_id} — auto-generating…")
        model_ver = _auto_generate_forecast(db, product_id)
        if model_ver:
            rows = db.execute(
                select(DemandForecast)
                .where(DemandForecast.product_id == product_id)
                .order_by(DemandForecast.forecast_date)
            ).scalars().all()
        else:
            msg = {"warning": "Not enough sales history to generate forecast (need >= 30 days)."}
            _log("get_forecast", str(product_id), json.dumps(msg))
            return json.dumps(msg)

    total_pred = sum(float(r.predicted_demand) for r in rows)
    data = {
        "product_id": product_id,
        "forecast_days": len(rows),
        "total_predicted": round(total_pred, 1),
        "avg_daily_predicted": round(total_pred / len(rows), 1),
        "model": rows[0].model_version,
        "first_date": str(rows[0].forecast_date),
        "last_date": str(rows[-1].forecast_date),
    }
    _log("get_forecast", str(product_id), json.dumps(data))
    return json.dumps(data)


def tool_get_weather(location: str = "New York") -> str:
    """Fetch live weather to factor into supply-chain decisions."""
    data = fetch_current_weather(location)
    if not data or "error" in (data or {}):
        fallback = {"note": "Weather data unavailable", "location": location}
        _log("get_weather", location, json.dumps(fallback))
        return json.dumps(fallback)
    _log("get_weather", location, json.dumps(data))
    return json.dumps(data)


def tool_search_risks(query: str) -> str:
    hits = search_risks(query, n_results=3)
    _log("search_risks", query, json.dumps(hits[:2]))
    return json.dumps(hits)


def tool_select_supplier(db: Session, product_id: int) -> str:
    info = select_best_supplier(db, product_id)
    if not info:
        return json.dumps({"error": "No supplier linked to this product"})
    _log("select_supplier", str(product_id), json.dumps(info))
    return json.dumps(info)


def tool_create_po(db: Session, product_id: int, quantity: int, reasoning: str) -> str:
    sup = select_best_supplier(db, product_id)
    if not sup:
        return json.dumps({"error": "No supplier found"})
    po = draft_purchase_order(db, product_id, quantity, sup, reasoning)
    _log("create_po", f"pid={product_id} qty={quantity}", json.dumps(po))
    return json.dumps(po)

# ── DAY 4 END ────────────────────────────────────────────────────────


# ── DAY 4 START: ReAct agent orchestration ───────────────────────────

SYSTEM_PROMPT = """You are a Supply Chain Optimization Agent for an agricultural / retail business.
Your job is to monitor inventory, interpret demand forecasts, assess supply-chain risks,
factor in current weather conditions, and autonomously draft Purchase Orders when stock is low.

You must think step-by-step (chain of thought) before making decisions:
1. Check current inventory for the product (quantity on hand, safety stock, ROP, EOQ).
2. Review the demand forecast — how much will be sold in the next 30 days?
3. Check weather conditions — extreme weather (drought, storms, floods, heat waves) can
   disrupt supply, damage crops, delay transportation, or spike demand.
4. Search for relevant supply chain risks (port delays, strikes, pest outbreaks, etc.).
5. Calculate if stock will last through lead time + safety buffer.
6. Select the best supplier by balancing price (35%), reliability (35%), and lead-time (30%).
7. If reorder is needed, draft a PO with a clear justification.

IMPORTANT:
- If weather shows extreme conditions (heavy rain, storms, high temperature, drought),
  factor that into urgency and consider ordering MORE than EOQ.
- If risk alerts mention pest outbreaks, floods, or transportation strikes,
  mention those explicitly in your reasoning.
- For crops/perishable items, weather and risk are CRITICAL factors.

Always explain your reasoning before creating a PO.
End with exactly: DECISION: REORDER <qty> or DECISION: NO_REORDER
"""


def run_agent_for_product(db: Session, product_id: int, weather_location: str = "New York") -> dict:
    """
    Full ReAct-style agent loop for one product.
    Uses OpenAI chat to reason, then calls tools based on reasoning.
    Returns the full chain-of-thought + actions taken.
    """
    global _TOOL_LOG
    _TOOL_LOG = []

    settings = get_settings()
    api_key = settings.openai_api_key

    # 1. Gather context via tools
    inv_json = tool_check_inventory(db, product_id)
    inv_data = json.loads(inv_json)
    if "error" in inv_data:
        return {"error": inv_data["error"], "reasoning": "", "actions": []}

    forecast_json = tool_get_forecast(db, product_id)
    forecast_data = json.loads(forecast_json)

    weather_json = tool_get_weather(weather_location)
    weather_data = json.loads(weather_json)

    risk_json = tool_search_risks(
        f"supply disruption risk for {inv_data.get('product_name', 'product')}"
    )

    supplier_json = tool_select_supplier(db, product_id)
    supplier_data = json.loads(supplier_json)

    # 2. Build LLM prompt with full context
    context = (
        f"## Inventory Status\n{json.dumps(inv_data, indent=2)}\n\n"
        f"## Demand Forecast (Prophet / Seasonal-Naive)\n{json.dumps(forecast_data, indent=2)}\n\n"
        f"## Current Weather at '{weather_location}'\n{json.dumps(weather_data, indent=2)}\n\n"
        f"## Risk Intelligence\n{risk_json}\n\n"
        f"## Best Supplier Candidate\n{json.dumps(supplier_data, indent=2)}\n\n"
        f"Today's date: {date.today()}\n\n"
        "Based on ALL the above data (inventory, forecast, weather, risks, supplier),\n"
        "analyze whether this product needs restocking.\n"
        "If yes, recommend a PO quantity (use EOQ or adjust based on forecast/risk/weather).\n"
        "Provide step-by-step reasoning.\n"
        "End with: DECISION: REORDER <qty> or DECISION: NO_REORDER"
    )

    # 3. Call OpenAI
    reasoning = ""
    decision = "NO_REORDER"
    reorder_qty = 0

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)

        resp = client.chat.completions.create(
            model=settings.agent_llm_model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": context},
            ],
            temperature=settings.agent_temperature,
            max_tokens=1200,
        )
        reasoning = resp.choices[0].message.content or ""

        if "DECISION: REORDER" in reasoning.upper():
            import re
            match = re.search(r"DECISION:\s*REORDER\s+(\d+)", reasoning, re.IGNORECASE)
            if match:
                reorder_qty = int(match.group(1))
                decision = "REORDER"
            else:
                reorder_qty = inv_data.get("eoq_calc", 50)
                decision = "REORDER"
        else:
            decision = "NO_REORDER"

    except Exception as e:
        logger.warning(f"OpenAI call failed: {e}")
        reasoning = (
            f"[Fallback — OpenAI unavailable: {e}]\n\n"
            f"Product: {inv_data.get('product_name')}\n"
            f"Stock: {inv_data.get('quantity_on_hand')} | "
            f"ROP: {inv_data.get('reorder_point_calc')} | "
            f"EOQ: {inv_data.get('eoq_calc')}\n"
            f"Forecast 30d demand: {forecast_data.get('total_predicted', '?')}\n"
            f"Weather: {weather_data.get('condition', '?')} "
            f"Temp: {weather_data.get('temp_c', '?')}°C\n"
        )
        if inv_data.get("needs_reorder"):
            decision = "REORDER"
            reorder_qty = inv_data.get("eoq_calc", 50)
            reasoning += f"\nStock below ROP → DECISION: REORDER {reorder_qty}"
        else:
            decision = "NO_REORDER"
            reasoning += "\nStock above ROP → DECISION: NO_REORDER"

    # 4. Execute PO if needed
    po_result = None
    if decision == "REORDER" and reorder_qty > 0 and "error" not in supplier_data:
        po_json = tool_create_po(db, product_id, reorder_qty, reasoning[:500])
        po_result = json.loads(po_json)

    return {
        "product_id": product_id,
        "product_name": inv_data.get("product_name", ""),
        "decision": decision,
        "reorder_qty": reorder_qty,
        "reasoning": reasoning,
        "inventory": inv_data,
        "forecast": forecast_data,
        "weather": weather_data,
        "supplier": supplier_data,
        "purchase_order": po_result,
        "tool_log": list(_TOOL_LOG),
    }


def run_agent_scan_all(db: Session, weather_location: str = "New York") -> list[dict]:
    """Scan all products with stock below ROP and run agent for each."""
    products = db.execute(
        select(Product.product_id, Product.name, Inventory.quantity_on_hand, Inventory.reorder_point)
        .join(Inventory, Inventory.product_id == Product.product_id)
        .where(Inventory.quantity_on_hand <= Inventory.reorder_point)
    ).all()

    results = []
    for pid, name, qoh, rop in products:
        result = run_agent_for_product(db, pid, weather_location)
        results.append(result)
    return results

# ── DAY 4 END ────────────────────────────────────────────────────────
