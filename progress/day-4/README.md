# Day 4 — Agent Orchestration & PO Generation (20 Marks)

## Focus Area
Integration & Stability — LangChain ReAct agent with OpenAI GPT-4o-mini.

## What Was Built

### PO Generation Service (`backend/app/services/po_generation_service.py`)
- **ROP (Reorder Point)** = avg_daily_demand × lead_time_days + safety_stock
- **EOQ (Economic Order Quantity)** = √(2 × annual_demand × ordering_cost / holding_cost)
- **Supplier scoring** = 35% reliability + 35% price + 30% lead-time efficiency
- **PO drafting** — creates `PurchaseOrder` + `PurchaseOrderItem` in DB

### Agent Service (`backend/app/services/agent_service.py`)
- ReAct-style agent that calls tools to gather context and then decides:
  1. `check_inventory` — stock levels, ROP, EOQ
  2. `get_forecast` — reads stored forecasts from DB, and if missing auto-runs Prophet
  3. `get_weather` — fetches live weather (WeatherAPI) using the provided location
  4. `search_risks` — ChromaDB semantic risk search (Risk RAG)
  5. `select_supplier` — composite supplier scoring (price/reliability/lead-time)
- Sends full context to **OpenAI GPT-4o-mini** with weather-aware chain-of-thought prompt
- Parses `DECISION: REORDER <qty>` or `DECISION: NO_REORDER`
- Auto-drafts PO when reorder triggered
- **Fallback**: if OpenAI fails, uses deterministic ROP/EOQ logic

### Agent Router (`backend/app/routers/agent.py`)
- `GET /api/v1/agent/stock-analysis/{product_id}` — ROP/EOQ without LLM
- `POST /api/v1/agent/run/{product_id}?location=...` — full agent loop with weather-aware context
- `POST /api/v1/agent/scan?location=...` — scan all below-ROP products with weather-aware context
- `GET /api/v1/agent/po-history` — agent-generated PO list

### Frontend (`frontend/app.py` — Agent Orchestration page)
- Single product stock analysis (ROP/EOQ metrics)
- Full agent run with chain-of-thought display
- Bulk scan of all low-stock products
- PO history table with reasoning expanders
- Tool call debug log
- Weather location input to drive weather-aware decisions

### Farming / Crops Dataset for Demo
- Added `database/seed_farming.py` to create a “farmer crops” dataset:
  - 15 crop products
  - mixed inventory zones: above ROP, below ROP, and below safety stock (critical)
  - agriculture-specific risk alerts (drought, pest outbreak, floods, heatwave, etc.)
- Added backend endpoint: `POST /api/v1/data-sources/load-farming`
- Added frontend button in Data Manager to load this dataset quickly for demos

## Prompt Tuning Log
1. Initial prompt asked for generic analysis — agent produced vague reasoning.
2. Added explicit supplier scoring weights (35/35/30) — improved specificity.
3. Required strict output end format: `DECISION: REORDER <qty>` or `DECISION: NO_REORDER` — improved parsing reliability.
4. Added weather + extreme-condition instructions — improved “order/no-order” decisions for perishable crops.
5. Set temperature to 0.3 — reduced variance in deterministic decisions.

## KPIs
- **End-to-end integration (8)**: DB → forecast → LLM prompt → PO draft
- **Stability (4)**: Fallback if OpenAI fails, try/except at every stage
- **Output quality (4)**: Clear chain-of-thought with supplier justification
- **Debugging effort (4)**: Tool call log, prompt tuning history above
