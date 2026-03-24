# Day 2 — Data integration & skeleton pipeline

**Status:** Not started (update this file when done.)

## Planned work

- PostgreSQL running; apply [`database/schema.sql`](../../database/schema.sql).
- Ingest mock POS / inventory data (ERP simulation).
- Integrate **WeatherAPI** (`WEATHERAPI_KEY`) and expose or use from backend.
- Streamlit: show raw historical tables from DB + weather sample.

## Deliverables checklist

- [ ] DB initializes without errors; FastAPI connects.
- [ ] Live weather pull works for a location query.
- [ ] Streamlit shows raw sales/inventory data from DB.

## When finished

Add links to new/changed files (e.g. seed scripts, `routers/weather.py`) and a short demo note.

Commit example: `feat: day-2 mock data ingestion + weather + streamlit raw views`
