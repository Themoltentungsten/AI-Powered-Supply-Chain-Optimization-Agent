# Day 2 — Data integration & skeleton pipeline

**Status:** Done

## Completed work

- Switched database layer from async PostgreSQL to **sync SQLAlchemy + SQLite** for zero-config local dev (`backend/app/database.py`).
- Created **`database/seed_data.py`** — generates 10 products with realistic seasonal profiles, 5 suppliers, product-supplier mappings, inventory records, **2+ years of daily sales history** with seasonality/trend/promotions/noise, and 10 historical risk events.
- Integrated **WeatherAPI.com** — endpoint `GET /api/v1/weather?q=CityName` fetches live weather (temp, humidity, precipitation, wind).
- Created `backend/app/services/weather_service.py` for reusable weather fetch logic.
- Updated all routers to sync `Session` (was `AsyncSession`).
- Streamlit now shows **raw inventory tables**, **sales-history charts**, and a **Weather** page with live data.

## Files changed / created

| File | Action |
|------|--------|
| `backend/app/config.py` | Updated — SQLite default, weather config |
| `backend/app/database.py` | Updated — sync engine, SQLite pragma |
| `backend/app/routers/inventory.py` | Updated — sync |
| `backend/app/routers/forecasting.py` | Updated — sync |
| `backend/app/routers/purchase_orders.py` | Updated — sync |
| `backend/app/routers/weather.py` | Updated — sync httpx |
| `backend/app/services/weather_service.py` | **New** |
| `database/seed_data.py` | **New** |
| `frontend/app.py` | Updated — raw data tables, weather page |

## How to verify

```bash
python database/seed_data.py          # populates supply_chain.db
uvicorn backend.app.main:app --reload # start API
streamlit run frontend/app.py         # open dashboard
# Visit Inventory page → raw table; Weather page → enter city
```
