# Day 1 — Problem & planning

**Focus:** Problem statement, architecture, PostgreSQL outline, FastAPI + Streamlit initialization.

## Deliverables (completed)

| Item | Location in repo |
|------|------------------|
| Formal project document (problem, features, scope, roles) | [`docs/PROJECT_DOCUMENT.md`](../../docs/PROJECT_DOCUMENT.md) |
| System architecture diagram (source + PNG) | [`docs/architecture_diagram.py`](../../docs/architecture_diagram.py) — run to generate `docs/architecture_diagram.png` |
| PostgreSQL schema | [`database/schema.sql`](../../database/schema.sql) |
| FastAPI app + routers | [`backend/app/`](../../backend/app/) |
| Streamlit dashboard skeleton | [`frontend/app.py`](../../frontend/app.py) |
| Root README + day-wise plan | [`README.md`](../../README.md) |

## KPI alignment

- **Problem clarity:** SMBs lose **5–15% revenue** from inventory mismatch (overstock waste / stockout lost sales).
- **Scope:** MVP uses **Prophet** for forecasting; complex **LSTM** deferred post-MVP.
- **Architecture flow:** Data integration → Demand forecasting → Agent orchestration → Streamlit dashboard.
- **Roles:** Data/Forecasting (Prophet), Backend/Agents (LangChain), Frontend (Streamlit/Plotly).

## Environment notes

- Day 1 Python deps: see [`requirements.txt`](../../requirements.txt).
- Weather provider for later days: **WeatherAPI** (`WEATHERAPI_KEY` in `.env.example`), not OpenWeather.

## How to verify locally

```bash
pip install -r requirements.txt
# Set up PostgreSQL + .env, then:
uvicorn backend.app.main:app --reload --port 8000
streamlit run frontend/app.py
```

## Git

Commit example: `chore: day-1 project doc, schema, fastapi, streamlit skeleton`
