# Day 3 — Core forecasting & RAG

**Status:** Done

## Completed work

- Implemented **Prophet** demand forecasting with yearly + weekly seasonality, multiplicative mode, promotion regressor, and confidence intervals (`backend/app/services/forecasting_service.py`).
- Built **seasonal-naive numpy fallback** that runs automatically if Prophet is not installed — still produces seasonal graphs with confidence bands.
- Created **lightweight RAG pipeline** using ChromaDB over historical supply-chain risk events (`backend/app/services/risk_rag_service.py`).
- Added `POST /api/v1/forecasts/generate/{product_id}` — trains model on historical sales, stores forecast in DB.
- Added `GET /api/v1/risks` and `GET /api/v1/risks/search?q=...` — list and semantic-search risk events.
- Streamlit **Demand Forecasting** page shows historical sales + forecast graph with confidence intervals.
- Streamlit **Risk Alerts** page shows risk event table + RAG-powered natural-language search.

## Files changed / created

| File | Action |
|------|--------|
| `backend/app/services/forecasting_service.py` | **New** — Prophet + fallback |
| `backend/app/services/risk_rag_service.py` | **New** — ChromaDB RAG |
| `backend/app/routers/forecasting.py` | Updated — POST generate endpoint |
| `backend/app/routers/risk.py` | **New** — risk list + RAG search |
| `backend/app/main.py` | Updated — risk router, RAG init at startup |
| `frontend/app.py` | Updated — forecast UI, risk search UI |

## How to verify

```bash
# Start backend (seeds + indexes ChromaDB at startup)
uvicorn backend.app.main:app --reload

# Open Streamlit
streamlit run frontend/app.py

# Demand Forecasting page → select product → click Run Forecast
# Risk Alerts page → type "supplier delay" → see semantic results
```
