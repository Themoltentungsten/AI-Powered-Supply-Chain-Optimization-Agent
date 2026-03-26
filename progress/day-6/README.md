# Day 6 — Final Live Demo & Q&A Defense

**Status:** Done  
**Focus:** Live demo execution, seasonal trend validation, Q&A preparation

---

## Deliverables

### 1. Demo Script

**Step-by-step live demo flow:**

1. **Data Manager** → Click "Load Farming / Crops Dataset"
   - Shows 15 crops with mixed stock levels
   - 10 agriculture-specific risk events loaded
   - Point out: some products are critical (below safety stock), some below ROP, some healthy

2. **Dashboard** → Show real-time overview
   - 5 KPI cards including critical stockout count
   - Inventory bar chart with ROP/safety lines
   - **Stockout prediction timeline** — red bars = critical, yellow = warning
   - Active risk alerts prominently displayed

3. **Demand Forecasting** → Select a crop (e.g., "Basmati Rice")
   - Click "Run Forecast" → Prophet generates 30-day prediction
   - Show the seasonal trend in the confidence interval chart
   - Point out: multiplicative seasonality captures harvest/planting cycles

4. **Agent Orchestration** → Set location to "Mumbai"
   - Select a critical product (e.g., "Corn / Maize")
   - Click "Run Full Agent (OpenAI)"
   - Walk through the chain-of-thought reasoning:
     - Inventory status (below ROP)
     - Forecast demand (next 30 days)
     - Weather context (monsoon/heat impact)
     - Risk alerts (drought, pest outbreak)
     - Supplier selection (price 35%, reliability 35%, lead-time 30%)
     - Decision: REORDER with quantity and justification
   - Show the drafted Purchase Order with supplier, quantity, total cost

5. **Agent Orchestration** → Click "Run Full Scan"
   - Agent processes all below-ROP products
   - Shows reorder/no-reorder decisions with reasoning for each
   - Multiple POs drafted automatically

6. **Savings Report** → Show business impact
   - Monthly savings projection in dollars
   - Overstock waste vs stockout loss breakdown
   - Top products by savings potential
   - Business narrative: "The agent can save $X/month"

7. **Risk Alerts** → Search "drought" using RAG
   - ChromaDB semantic search finds relevant risk events
   - Show severity distribution pie chart

### 2. Seasonal Trend Demonstration

The farming dataset includes seasonal patterns:
- Grains peak around harvest season (day 90-300)
- Fruits peak in summer (day 150-200)
- Spices/cotton have their own seasonal amplitudes
- Prophet's multiplicative seasonality mode captures these patterns clearly in the forecast charts

### 3. Q&A Defense Points

| Question | Answer |
|----------|--------|
| Why Prophet over LSTM? | Prophet handles seasonality natively, works with limited data (1 year), auto-detects holidays. LSTM needs large datasets and manual feature engineering. |
| How does the ReAct agent work? | It follows a Reasoning + Acting loop: check inventory → get forecast → fetch weather → search risks → score suppliers → make REORDER/NO_REORDER decision. |
| What is RAG? | Retrieval-Augmented Generation — risk events are embedded in ChromaDB as vectors, then semantically searched when the agent needs risk context. |
| How is supplier scored? | Composite: 35% reliability + 35% price competitiveness + 30% lead-time efficiency. |
| What if OpenAI fails? | Deterministic fallback uses ROP/EOQ math to decide reorder without the LLM. |
| What is ROP? | Reorder Point = avg_daily_demand × lead_time + safety_stock. |
| What is EOQ? | Economic Order Quantity = sqrt(2 × annual_demand × ordering_cost / holding_cost). |
| How does weather affect decisions? | Extreme weather (drought, storms) increases urgency — agent may order MORE than EOQ for perishable crops. |

---

## KPI Alignment

| KPI | Score Target | How Addressed |
|-----|-------------|---------------|
| Demo success (4) | Live dashboard, agent drafts PO on low-stock | Full walkthrough from data load → forecast → agent reasoning → PO generation |
| Q&A defense (3) | Technical architecture defense | Prepared answers for Prophet, ReAct, RAG, ROP/EOQ, supplier scoring, fallback |
| Presentation quality (3) | Smooth flow, clear narrative | Step-by-step script, role assignments, business impact framing |
