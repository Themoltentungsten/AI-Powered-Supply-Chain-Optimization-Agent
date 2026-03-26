# AI-Powered Supply Chain Optimization Agent

An agentic AI system that monitors inventory levels, forecasts demand using historical data and external signals, automatically generates purchase orders, identifies supply chain risks, and presents insights through an interactive real-time dashboard.

## Problem

Small and medium businesses lose **5-15% of revenue** due to inventory mismanagement — overstocking causes waste while stockouts cause lost sales. This system automates demand planning and procurement using Prophet forecasting and a LangChain ReAct agent.

## Architecture

```
Data Integration → Demand Forecasting → Agent Orchestration → Streamlit Dashboard
```

| Layer | Technology |
|---|---|
| Frontend | Streamlit + Plotly |
| Backend | FastAPI |
| Agent | LangChain ReAct |
| Forecasting | Prophet |
| Database | PostgreSQL |
| LLM | GPT-4o |

## Project Structure

```
├── backend/
│   └── app/
│       ├── main.py              # FastAPI application entry point
│       ├── config.py            # Settings and environment config
│       ├── database.py          # SQLAlchemy engine (PostgreSQL or SQLite)
│       ├── models/
│       │   └── schema.py        # SQLAlchemy ORM models
│       ├── routers/
│       │   ├── health.py        # Health check endpoint
│       │   ├── inventory.py     # Inventory CRUD endpoints
│       │   ├── forecasting.py   # Sales history & forecast endpoints
│       │   └── purchase_orders.py  # PO management endpoints
│       └── services/            # Business logic (Day 3-4)
├── frontend/
│   └── app.py                   # Streamlit dashboard
├── database/
│   └── schema.sql               # PostgreSQL DDL schema
├── docs/
│   └── PROJECT_DOCUMENT.md      # Formal project document
├── progress/
│   ├── README.md                # Day-wise progress index
│   └── day-1 … day-6/           # One README per day (artifacts + checklist)
├── requirements.txt
├── .env.example
└── README.md
```

## Progress on GitHub

Day-by-day documentation lives under [`progress/`](progress/). Start at [`progress/README.md`](progress/README.md), then open `progress/day-N/README.md` for that day’s deliverables and file links. When you finish a day, update its README and commit (e.g. `docs: day-2 data integration`).

## Day-Wise Work Plan

| Day | Focus Area | Technical Tasks | Deliverables |
|---|---|---|---|
| Day 1 | Problem & Planning | Define system architecture linking data layer, Prophet forecasting, and LangChain ReAct agent. Outline PostgreSQL schema for inventory, sales history, and purchase orders. Initialize FastAPI and Streamlit apps. | Formal project document with problem statement, feature list, architecture diagram, and team roles. |
| Day 2 | Data Integration & Skeleton Pipeline | Set up PostgreSQL and ingest mock historical POS/inventory data. Integrate external weather (e.g. [WeatherAPI](https://www.weatherapi.com/)). Scaffold data view in Streamlit. | Running skeleton: backend fetches DB + weather API data and displays raw tables/charts in Streamlit. |
| Day 3 | Core Forecasting & RAG Features | Implement Prophet for daily/weekly rolling forecasts with confidence intervals. Build lightweight RAG pipeline over historical supply chain incidents. | Functional forecast engine + risk retrieval module with test cases and holdout validation. |
| Day 4 | Agent Orchestration & PO Generation | Implement ROP/EOQ logic. Set up LangChain ReAct tools to query inventory, run forecast, generate PO, and retrieve risk intelligence. | End-to-end internal pipeline where agent monitors stock and drafts purchase orders. |
| Day 5 | Dashboard, Polish & Storytelling | Finalize Streamlit UI with Plotly charts for stock, forecast, and risk alerts. Add monthly savings visualization and polish UX for demo. | Demo-ready dashboard with clean visuals, active scenario, and business impact narrative. |
| Day 6 | Final Live Demo & Q&A Defense | Run live walkthrough with seasonal demand scenario. Prepare role-based speaking flow and backup demo video. | Successful end-to-end demo and clear defense of technical choices (Prophet, ReAct, RAG). |

### Day 1 KPI Alignment

- **Clarity of problem:** SMBs lose **5-15% revenue** due to overstocking and stockouts.
- **Feasible scope:** MVP uses **Prophet** for seasonality forecasting; LSTM is post-MVP.
- **Architecture understanding:** Pipeline is **Data Integration -> Demand Forecasting -> Agent Orchestration -> Streamlit Dashboard**.
- **Team roles defined:** Clear ownership for Data/Forecasting, Backend/Agents, and Frontend/Visualization.

## Quick Start (PostgreSQL)

The app is intended to run against **PostgreSQL** (see `DATABASE_URL` in `.env`). Tables and seed data are created by the Python seed script; you do not need to run `schema.sql` manually unless you prefer raw SQL.

### 1. Install PostgreSQL and `psql`

- Install [PostgreSQL for Windows](https://www.postgresql.org/download/windows/) (or `winget install PostgreSQL.PostgreSQL.18`).
- Ensure `psql` is on your PATH (default: `C:\Program Files\PostgreSQL\<version>\bin`).

### 2. Create the database

**Windows (PowerShell)** — use `psql` as the superuser (adjust user/host if yours differ):

```powershell
$env:PGPASSWORD = "your_postgres_password"
psql -U postgres -h localhost -p 5432 -d postgres -c "CREATE DATABASE supply_chain;"
```

**macOS / Linux:**

```bash
createdb supply_chain
# or: psql -U postgres -c "CREATE DATABASE supply_chain;"
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

This includes **`psycopg2-binary`** so SQLAlchemy can connect to PostgreSQL.

### 4. Configure environment

**Windows (PowerShell):** `Copy-Item .env.example .env`  
**macOS / Linux:** `cp .env.example .env`

Edit `.env` and set:

- **`DATABASE_URL`** — must point at your PostgreSQL instance, e.g.  
  `postgresql://postgres:YOUR_PASSWORD@localhost:5432/supply_chain`  
  (Use a single `DATABASE_URL` line; duplicate keys override each other.)

- **`WEATHERAPI_KEY`** — from [WeatherAPI.com](https://www.weatherapi.com/) (optional for weather pages).

Keep `.env` local; it is gitignored.

### 5. Create tables and load data (one DB: your `DATABASE_URL`)

Everything below writes to the **same** database as in `.env` (PostgreSQL or SQLite). Pick one path for testing.

| Goal | Command |
|------|---------|
| **Synthetic demo** (seasonal mock data + risk events) | `python database/load_project_data.py seed` |
| Re-run synthetic after Kaggle / old seed | `python database/load_project_data.py seed --replace` |
| **Kaggle** (Superstore preset, needs [Kaggle API](https://github.com/Kaggle/kaggle-api/blob/main/docs/README.md) + `kagglehub`) | `python database/load_project_data.py kaggle` |
| Kaggle Online Retail preset | `python database/load_project_data.py kaggle --preset online-retail` |
| **Local CSV** (Superstore- or Online-Retail-shaped) | `python database/load_project_data.py csv --path "C:\path\to\file.csv"` |

Optional limits: add `--max-products 80` to `kaggle` or `csv` subcommands.

After a **Kaggle** or **csv** import, restart the backend and regenerate forecasts in the UI (`demand_forecasts` is cleared on import).

Details and column detection: docstring in `database/import_kaggle_retail.py`.

Legacy one-offs (still valid): `python database/seed_data.py`, `python database/fetch_superstore_kagglehub.py`, `python database/import_kaggle_retail.py --csv ...`.

### 6. Start the backend

```bash
uvicorn backend.app.main:app --reload --port 8000
```

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 7. Start the frontend

```bash
streamlit run frontend/app.py
```

### Optional: SQLite only for quick tests

If you temporarily use SQLite, set in `.env`:

```env
DATABASE_URL=sqlite:///./supply_chain.db
```

Then run `python database/seed_data.py` again. For coursework / demos aligned with the project spec, prefer **PostgreSQL**.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| GET | `/api/v1/products` | List all products |
| GET | `/api/v1/inventory` | List inventory with reorder status |
| GET | `/api/v1/inventory/{id}` | Get inventory for a product |
| GET | `/api/v1/sales-history/{id}` | Get sales history |
| GET | `/api/v1/forecasts/{id}` | Get demand forecasts |
| GET | `/api/v1/purchase-orders` | List purchase orders |
| GET | `/api/v1/purchase-orders/{id}` | Get PO details with line items |
| GET | `/api/v1/weather?q=` | Current weather from [WeatherAPI](https://www.weatherapi.com/) (uses `WEATHERAPI_KEY` in `.env`) |
| GET | `/api/v1/agent/stock-analysis/{id}` | ROP / EOQ analysis for a product |
| POST | `/api/v1/agent/run/{id}` | Run ReAct agent for a product (OpenAI) |
| POST | `/api/v1/agent/scan` | Scan all below-ROP products and auto-draft POs |
| GET | `/api/v1/agent/po-history` | List agent-generated POs with reasoning |

## Team Roles

| Role | Responsibility |
|---|---|
| Data & Forecasting Lead | PostgreSQL, mock data, Prophet model |
| Backend & Agent Lead | FastAPI, LangChain ReAct agent, RAG pipeline |
| Frontend & Visualization Lead | Streamlit dashboard, Plotly charts, UX |
