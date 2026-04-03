# AI-Powered Supply Chain Optimization Agent

## Project Document — Day 1 Deliverable

---

## 1. Problem Statement

Small and medium businesses (SMBs) lose **5–15% of annual revenue** due to inventory mismanagement. This manifests in two costly failure modes:

| Failure Mode | Business Impact |
|---|---|
| **Overstocking** | Capital tied up in excess inventory, increased warehousing costs, product waste/expiry |
| **Stockouts** | Lost sales, damaged customer loyalty, emergency procurement at premium prices |

Most SMBs rely on manual spreadsheet-based reordering or simple min/max thresholds that ignore seasonality, external signals (weather, promotions, events), and supplier reliability. They lack the data science teams that large enterprises use for demand planning.

**Our solution** is an agentic AI system that continuously monitors inventory levels, forecasts demand using historical sales data and external signals, automatically generates purchase orders when stock falls below computed reorder points, identifies supply chain risks from news and weather feeds, and presents all insights through an interactive real-time dashboard.

---

## 2. Feature List

### 2.1 MVP Features (5-Day Scope)

| # | Feature | Description |
|---|---|---|
| F1 | **Real-Time Inventory Dashboard** | Streamlit + Plotly dashboard showing current stock levels, reorder points, and predicted stockout dates for every product |
| F2 | **Demand Forecasting** | Prophet-based time-series forecasting with daily/weekly granularity, confidence intervals, and external regressors (weather, promotions) |
| F3 | **Automated Purchase Order Generation** | When inventory drops below the computed Reorder Point (ROP), the system auto-drafts a Purchase Order selecting the optimal supplier by price, lead time, and reliability |
| F4 | **Supply Chain Risk Identification** | RAG pipeline over historical incidents + live weather/news APIs to flag risks (e.g., "Supplier X has 30% chance of delay due to port congestion") |
| F5 | **LangChain ReAct Agent Orchestration** | Central agent that reasons with chain-of-thought ("Stock is X, forecast demand is Y, lead time is Z…") and invokes tools: query inventory, run forecast, generate PO, search risk intelligence |
| F6 | **Monthly Savings Report** | Dashboard page summarizing waste reduction, stockout events prevented, and overall cost optimization |

### 2.2 Out of Scope (Post-MVP)

- LSTM-based deep learning forecasting (complex, requires more data)
- Real ERP/POS integration (we use realistic mock data)
- Multi-warehouse routing optimization
- Mobile application

### 2.3 MVP Scoping Rationale

For the MVP we focus on **Prophet for seasonality forecasting** rather than building complex LSTMs. Prophet is ideal because:
- Handles clear seasonality patterns with less data
- Built-in support for holidays and external regressors
- Faster training and easier interpretability
- Sufficient accuracy for the SMB use case

---

## 3. System Architecture

### 3.1 High-Level Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        STREAMLIT DASHBOARD                              │
│  ┌──────────┐ ┌──────────────┐ ┌──────────┐ ┌───────────────────────┐  │
│  │ Inventory│ │  Forecasting │ │   Risk   │ │  Purchase Orders &    │  │
│  │ Overview │ │   Graphs     │ │  Alerts  │ │  Savings Report       │  │
│  └────┬─────┘ └──────┬───────┘ └────┬─────┘ └──────────┬────────────┘  │
│       │              │              │                   │               │
└───────┼──────────────┼──────────────┼───────────────────┼───────────────┘
        │              │              │                   │
        ▼              ▼              ▼                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND                                  │
│                                                                         │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │                  LANGCHAIN ReAct AGENT                             │ │
│  │                                                                    │ │
│  │  Tools:                                                            │ │
│  │  ┌──────────────┐ ┌────────────┐ ┌──────────┐ ┌────────────────┐  │ │
│  │  │ Query        │ │ Run        │ │ Generate │ │ Search Risk    │  │ │
│  │  │ Inventory    │ │ Forecast   │ │ PO       │ │ Intelligence   │  │ │
│  │  └──────┬───────┘ └─────┬──────┘ └────┬─────┘ └───────┬────────┘  │ │
│  │         │               │             │               │            │ │
│  └─────────┼───────────────┼─────────────┼───────────────┼────────────┘ │
│            │               │             │               │              │
│  ┌─────────▼───────┐ ┌────▼──────┐ ┌────▼─────┐ ┌──────▼───────────┐  │
│  │ Inventory       │ │ Prophet   │ │ PO       │ │ RAG Pipeline     │  │
│  │ Service         │ │ Forecast  │ │ Generator│ │ (Risk Analysis)  │  │
│  │                 │ │ Engine    │ │          │ │                  │  │
│  └─────────┬───────┘ └────┬──────┘ └────┬─────┘ └──────┬───────────┘  │
│            │               │             │               │              │
└────────────┼───────────────┼─────────────┼───────────────┼──────────────┘
             │               │             │               │
             ▼               ▼             ▼               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATA LAYER                                      │
│                                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────────┐  │
│  │   PostgreSQL     │  │  External APIs   │  │  Document Store       │  │
│  │                  │  │                  │  │  (Risk RAG)           │  │
│  │  • products      │  │  • OpenWeather   │  │                       │  │
│  │  • inventory     │  │  • News feeds    │  │  • Historical         │  │
│  │  • sales_history │  │  • Commodity     │  │    incidents          │  │
│  │  • suppliers     │  │    prices        │  │  • Supplier reports   │  │
│  │  • purchase_     │  │                  │  │                       │  │
│  │    orders        │  │                  │  │                       │  │
│  └──────────────────┘  └──────────────────┘  └───────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Architecture Flow (Pipeline)

```
Data Integration → Demand Forecasting → Agent Orchestration → Streamlit Dashboard
```

**Step-by-step:**

1. **Data Integration**: PostgreSQL stores products, inventory levels, sales history, supplier info, and purchase orders. External APIs (OpenWeatherMap, news) provide real-time signals.

2. **Demand Forecasting**: Prophet consumes historical sales data + external regressors (weather, promotions) to produce rolling demand forecasts with confidence intervals at daily/weekly granularity.

3. **Agent Orchestration**: The LangChain ReAct agent acts as the central decision-maker. It uses chain-of-thought reasoning to:
   - Monitor stock levels against computed Reorder Points (ROP)
   - Interpret forecast output to anticipate future demand
   - Calculate Economic Order Quantities (EOQ)
   - Auto-generate Purchase Orders selecting optimal suppliers
   - Query the RAG pipeline for risk intelligence

4. **Streamlit Dashboard**: Interactive Plotly charts display inventory status, forecasting graphs with confidence intervals, risk alerts, PO history, and monthly savings reports.

### 3.3 Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit + Plotly | Interactive dashboards and data visualization |
| Backend API | FastAPI | REST API serving data to the frontend |
| Agent Framework | LangChain (ReAct) | Autonomous agent orchestration with tool use |
| Forecasting | Prophet | Time-series demand forecasting with seasonality |
| Risk Analysis | RAG (LangChain + ChromaDB) | Retrieval-augmented generation over incident data |
| LLM | GPT-4o (OpenAI) | Reasoning, PO drafting, risk summarization |
| Database | PostgreSQL | Persistent storage for all structured data |
| External APIs | OpenWeatherMap, News API | Weather data and news for risk signals |

---

## 4. Database Schema Overview

### Tables

| Table | Purpose |
|---|---|
| `products` | Master product catalog with categories and unit costs |
| `suppliers` | Supplier directory with reliability scores and lead times |
| `inventory` | Current stock levels, reorder points, last restock dates |
| `sales_history` | Daily point-of-sale transaction records |
| `purchase_orders` | Generated POs with supplier, quantity, status tracking |
| `purchase_order_items` | Line items within each purchase order |
| `risk_events` | Logged supply chain risk events for RAG and alerting |
| `weather_data` | Cached weather API responses used as forecast regressors |

Full SQL schema: see `database/schema.sql`

---

## 5. Team Roles & Responsibilities

| Role | Owner | Responsibilities |
|---|---|---|
| **Data & Forecasting Lead** | Team Member 1 | PostgreSQL schema design, mock data generation, Prophet model training/tuning, external regressor integration (weather), forecast accuracy validation |
| **Backend & Agent Lead** | Team Member 2 | FastAPI endpoints, LangChain ReAct agent setup, tool definitions (query inventory, run forecast, generate PO, risk search), ROP/EOQ calculations, RAG pipeline for risk analysis |
| **Frontend & Visualization Lead** | Team Member 3 | Streamlit dashboard layout, Plotly interactive charts (inventory, forecasting, risk alerts), PO display, monthly savings report, UX polish and demo preparation |
| **Integration & DevOps** | Shared | Git workflow, environment setup, end-to-end pipeline testing, deployment, documentation |

---

## 6. Day-by-Day Plan

| Day | Focus | Key Deliverables |
|---|---|---|
| **Day 1** | Problem & Planning | Project document, architecture diagram, DB schema, FastAPI + Streamlit init |
| **Day 2** | Data Integration & Skeleton | PostgreSQL setup, mock data ingestion, OpenWeatherMap integration, raw data in Streamlit |
| **Day 3** | Core Forecasting & RAG | Prophet demand forecasting, confidence intervals, RAG risk pipeline |
| **Day 4** | Agent Orchestration & PO | ROP/EOQ calculation, LangChain ReAct agent, automated PO generation |
| **Day 5** | Dashboards & Polish | Plotly charts, risk alerts UI, monthly savings report, demo prep |
| **Day 6** | Final Demo & Q&A | Live demo, technical defense, backup video |

---

## 7. Risk & Mitigation

| Risk | Likelihood | Mitigation |
|---|---|---|
| Prophet fails to converge on sparse data | Medium | Fallback to simple moving average; ensure mock data has realistic seasonality |
| OpenAI API rate limits during demo | Low | Cache agent responses; prepare offline fallback |
| PostgreSQL connection issues | Low | Use SQLite fallback for local development |
| Scope creep into LSTM | Medium | Strict MVP boundary — Prophet only for forecasting |

---

*Document prepared: Day 1 — AI-Powered Supply Chain Optimization Agent*
