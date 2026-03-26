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
- ReAct-style agent that calls four tools:
  1. `check_inventory` — stock levels, ROP, EOQ
  2. `get_forecast` — Prophet demand forecast summary
  3. `search_risks` — ChromaDB semantic risk search
  4. `select_supplier` — composite supplier scoring
- Sends full context to **OpenAI GPT-4o-mini** with chain-of-thought prompt
- Parses `DECISION: REORDER <qty>` or `DECISION: NO_REORDER`
- Auto-drafts PO when reorder triggered
- **Fallback**: if OpenAI fails, uses deterministic ROP/EOQ logic

### Agent Router (`backend/app/routers/agent.py`)
- `GET /api/v1/agent/stock-analysis/{product_id}` — ROP/EOQ without LLM
- `POST /api/v1/agent/run/{product_id}` — full agent loop
- `POST /api/v1/agent/scan` — scan all below-ROP products
- `GET /api/v1/agent/po-history` — agent-generated PO list

### Frontend (`frontend/app.py` — Agent Orchestration page)
- Single product stock analysis (ROP/EOQ metrics)
- Full agent run with chain-of-thought display
- Bulk scan of all low-stock products
- PO history table with reasoning expanders
- Tool call debug log

## Prompt Tuning Log
1. Initial prompt asked for generic analysis — agent produced vague reasoning.
2. Added explicit supplier scoring weights (35/35/30) — improved specificity.
3. Required `DECISION: REORDER <qty>` format — enabled reliable parsing.
4. Added risk context — agent now warns about delivery delays before ordering.
5. Set temperature to 0.3 — reduced variance in deterministic decisions.

## KPIs
- **End-to-end integration (8)**: DB → forecast → LLM prompt → PO draft
- **Stability (4)**: Fallback if OpenAI fails, try/except at every stage
- **Output quality (4)**: Clear chain-of-thought with supplier justification
- **Debugging effort (4)**: Tool call log, prompt tuning history above
