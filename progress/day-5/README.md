# Day 5 — Dashboards, Polish & Storytelling

**Status:** Done  
**Focus:** Dashboard enhancement, savings report, stockout predictions, demo prep

---

## Deliverables

### 1. Savings Report Backend (`backend/app/routers/savings.py`)
- New `GET /savings/report` endpoint
- Calculates per-product:
  - Average daily demand (90-day rolling)
  - Days of stock remaining
  - Predicted stockout date
  - Stockout risk classification (critical < 7d, warning < 14d, ok)
  - Overstock holding cost (20% annual carrying cost, monthly)
  - Stockout lost-sales estimate (50% of selling price × deficit)
  - Total potential savings
- Summary aggregations: critical/warning/ok counts, total savings, agent PO stats

### 2. Enhanced Dashboard (Frontend)
- 5-column KPI row with critical stockout count
- Inventory bar chart: bars color-coded red (below ROP) vs blue (healthy)
- **Stockout prediction timeline**: horizontal bar chart showing days-of-stock per product with critical (7d) and warning (14d) threshold lines
- Active risk alerts displayed prominently on dashboard
- Risk Alerts page now includes a severity distribution pie chart

### 3. Savings Report Page (Frontend)
- 8 KPI metrics: total savings, overstock cost, stockout cost, agent POs, critical/warning/healthy counts
- Donut chart: overstock waste vs lost sales breakdown
- Bar chart: top 10 products by savings potential, color-coded by risk
- Full product analysis table sorted by days-of-stock
- Business impact narrative with dollar figures and actionable insights

### 4. Purchase Orders Page Polish
- Added KPI row: total POs, agent-generated count, total value
- Better empty state messaging

### 5. Overall UI Polish
- Version bumped to v0.2.0
- Day 5 comment header added to frontend
- Consistent Plotly white template across all charts
- Better metric card organization and layout

---

## KPI Alignment

| KPI | Score Target | How Addressed |
|-----|-------------|---------------|
| UI clarity (3) | Plotly charts easy to read, risk alerts prominent | Stockout timeline with color-coded risk levels, risk alerts on dashboard, severity pie chart |
| Demo readiness (3) | Pre-loaded active stockout scenario | Farming dataset has products in critical/warning/ok zones, dashboard highlights them immediately |
| Storytelling (2) | Monthly savings report with business narrative | Savings page shows dollar-value impact: waste reduction, lost sales prevention, agent PO value |
| Feature completeness (2) | All systems working together | Forecasting → Agent → PO → Dashboard → Savings all integrated end-to-end |

---

## Files Changed

| File | Change |
|------|--------|
| `backend/app/routers/savings.py` | New — savings analysis endpoint |
| `backend/app/main.py` | Registered savings router |
| `frontend/app.py` | Enhanced dashboard, savings report, UI polish |
