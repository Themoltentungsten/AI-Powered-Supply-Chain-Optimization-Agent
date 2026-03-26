# About This Project (Hinglish Guide)

## 1) Project ka short intro

Ye project ek **AI-Powered Supply Chain Optimization Agent** hai jo SMBs (small-medium businesses) ke liye banaya gaya hai. Main problem:
- overstock ho gaya to paisa inventory me atak jata hai + waste
- stockout ho gaya to sales miss ho jati hai

Target: data + forecasting + risk intelligence use karke better inventory decisions lena.

Current progress: **Day 1, Day 2, Day 3, Day 4 complete**.

---

## 2) Important terms ka meaning (Hinglish Glossary)

Yeh section viva/presentation ke liye hai. Teacher agar koi term pooche, yeh short definitions use kar sakte ho:

- **FastAPI**: Python ka fast backend framework jisse hum API endpoints banate hain (jaise `/api/v1/inventory`).
- **API Endpoint**: Backend ka ek URL jahan specific kaam hota hai, e.g. weather laana, forecast generate karna.
- **Streamlit**: Python-based frontend tool jisse quickly dashboard/UI ban jata hai.
- **Plotly**: Interactive charts banane ki library (zoom, hover, filter support).
- **SQLAlchemy**: Python ORM jo database tables ko Python classes ke form me handle karta hai.
- **ORM (Object Relational Mapping)**: DB table aur Python object ke beech mapping.
- **PostgreSQL**: Production-grade relational DB — **is project ko run karne ke liye primary choice** (local ya server pe `DATABASE_URL` se connect).
- **SQLite**: Optional quick-test ke liye single file DB (`supply_chain.db`); coursework/demo ke liye README/`about.md` me **PostgreSQL prefer** karo.
- **psycopg2**: Python se PostgreSQL connect karne ka driver; `requirements.txt` me `psycopg2-binary` included hai.
- **Schema**: DB ka blueprint — kaunsi tables hongi, unke columns kya honge.
- **Seed Data**: Testing/demo ke liye auto-generate kiya gaya sample realistic data.
- **Demand Forecasting**: Past sales dekhkar future demand predict karna.
- **Prophet**: Time-series forecasting model (Meta ka) jo trend + seasonality handle karta hai.
- **Seasonality**: Time-based repeating pattern (e.g. winter me jacket sales up, summer me sunscreen up).
- **Confidence Interval**: Prediction ka expected range (upper/lower bounds), uncertainty show karta hai.
- **Fallback Model**: Backup model jo primary model fail hone pe run hota hai.
- **RAG (Retrieval-Augmented Generation)**: Pehle relevant info retrieve karo, phir answer/insight do.
- **ChromaDB**: Vector database jahan text embeddings store hote hain semantic search ke liye.
- **Semantic Search**: Keyword exact match ke bina meaning-based search.
- **Vector Embedding**: Text ka numeric representation jisse similarity compute hoti hai.
- **ROP (Reorder Point)**: Wo stock level jab naya order lagana chahiye = avg_daily_demand × lead_time + safety_stock. Agar current stock ≤ ROP → reorder trigger.
- **EOQ (Economic Order Quantity)**: Optimal kitna order karna chahiye jisse holding + ordering cost minimize ho = √(2 × annual_demand × order_cost / holding_cost).
- **LangChain**: Python framework jo LLMs (like GPT) ko tools aur data ke saath connect karta hai.
- **ReAct Agent**: "Reasoning + Acting" — agent sochta hai (chain-of-thought) phir tool call karta hai, loop me jab tak task complete na ho.
- **Chain-of-Thought (CoT)**: LLM step-by-step reasoning dikhata hai — "Stock X hai, forecast Y hai, lead time Z hai, isliye reorder karna chahiye."
- **GPT-4o-mini**: OpenAI ka lightweight fast model jo agent reasoning ke liye use hota hai.
- **Purchase Order (PO)**: Supplier ko bhejna wala official order — kitne units, kis price pe, kab delivery honi chahiye.
- **LangChain ReAct Agent**: Planned agent architecture (Day 4+) jahan model tools call karke step-by-step reason karega.
- **ROP (Reorder Point)**: Inventory level jahan naya order place karna chahiye.
- **EOQ (Economic Order Quantity)**: Optimal order quantity jo ordering + holding cost balance kare.
- **Stockout**: Product unavailable ho jana jab demand aaye.
- **Overstocking**: Extra inventory hold karna jo slow move/waste create kare.
- **External Regressor**: Forecast me external factor input (weather/promo) as influencing variable.
- **Smoke Test**: Quick basic functional test to ensure major endpoints run without crash.

---

## 3) Folder aur file ka full breakdown (kaun kya karta hai)

## `backend/`
FastAPI backend (API layer + business logic)

- `backend/app/main.py`
  - API app start hoti hai yahan se.
  - Routers register hote hain (`inventory`, `forecasting`, `purchase_orders`, `weather`, `risk`).
  - Startup pe DB tables init hoti hain aur risk RAG index warm-up hota hai.

- `backend/app/config.py`
  - Environment settings read karta hai (`.env` se).
  - Important configs:
    - `DATABASE_URL`
    - `WEATHERAPI_KEY`
    - app metadata

- `backend/app/database.py`
  - SQLAlchemy engine + session setup.
  - `get_db()` dependency routers me use hoti hai.
  - **PostgreSQL** (recommended) ya **SQLite** — jo bhi `.env` me `DATABASE_URL` ho.

- `backend/app/models/schema.py`
  - ORM models (DB tables ka Python version):
    - `Product`
    - `Supplier`
    - `ProductSupplier`
    - `Inventory`
    - `SalesHistory`
    - `PurchaseOrder`, `PurchaseOrderItem`
    - `RiskEvent`
    - `WeatherData`
    - `DemandForecast`

### `backend/app/routers/`
Yahan actual API endpoints defined hain:

- `health.py`
  - `GET /health` basic health check

- `inventory.py`
  - `GET /api/v1/products`
  - `GET /api/v1/inventory`
  - `GET /api/v1/inventory/{product_id}`

- `forecasting.py`
  - `GET /api/v1/sales-history/{product_id}`
  - `GET /api/v1/forecasts/{product_id}`
  - `POST /api/v1/forecasts/generate/{product_id}?periods=30`
    - yeh Day 3 ka core endpoint hai jo model run karta hai

- `purchase_orders.py`
  - `GET /api/v1/purchase-orders`
  - `GET /api/v1/purchase-orders/{po_id}`

- `weather.py`
  - `GET /api/v1/weather?q=Mumbai`
  - WeatherAPI se live weather laata hai (Day 2)

- `risk.py`
  - `GET /api/v1/risks`
  - `GET /api/v1/risks/search?q=port+delay`
  - RAG style semantic search for risk incidents (Day 3)

- `agent.py` (Day 4)
  - `GET /api/v1/agent/stock-analysis/{product_id}` — ROP/EOQ calculation (no LLM)
  - `POST /api/v1/agent/run/{product_id}` — full ReAct agent loop with OpenAI
  - `POST /api/v1/agent/scan` — scan all below-ROP products, auto-draft POs
  - `GET /api/v1/agent/po-history` — list agent-generated POs with reasoning

### `backend/app/services/`
Business logic layer:

- `weather_service.py` (Day 2)
  - WeatherAPI call helper

- `forecasting_service.py` (Day 3)
  - Prophet-based forecast logic
  - fallback seasonal-naive logic if Prophet unavailable

- `risk_rag_service.py` (Day 3)
  - ChromaDB based risk indexing + semantic retrieval

- `po_generation_service.py` (Day 4)
  - ROP / EOQ calculation formulas
  - Supplier composite scoring (35% reliability, 35% price, 30% lead-time)
  - PO drafting logic — creates PurchaseOrder + PurchaseOrderItem in DB

- `agent_service.py` (Day 4)
  - LangChain ReAct-style agent loop
  - 4 tools: check_inventory, get_forecast, search_risks, select_supplier
  - Sends context to OpenAI GPT-4o-mini for chain-of-thought reasoning
  - Parses REORDER/NO_REORDER decision, auto-drafts PO
  - Fallback: deterministic ROP/EOQ logic agar OpenAI fail ho

---

## `database/`

- `database/schema.sql`
  - formal SQL schema

- `database/seed_data.py`
  - Day 2 ka critical script
  - mock realistic dataset generate karta hai:
    - 10 products
    - 5 suppliers
    - 2+ years daily sales (seasonality + noise + trend)
    - 10 historical risk events

- `database/import_kaggle_retail.py`
  - Kaggle / retail CSV → `products`, `sales_history`, `inventory` (Superstore ya Online Retail format auto-detect)
  - Synthetic seed ki jagah real transactional patterns ke liye use karo

- `database/fetch_superstore_kagglehub.py`
  - `kagglehub` se dataset download + auto CSV pick + import (presets: `superstore`, `online-retail`)

- `database/load_project_data.py`
  - **Ek hi entry point:** `DATABASE_URL` (PostgreSQL ya SQLite) me ya to **synthetic seed** (`seed`) ya **Kaggle** (`kaggle`) ya **local CSV** (`csv`)

---

## `frontend/`

- `frontend/app.py` (Streamlit app)
  - Dashboard page
  - Inventory page (raw table + low stock)
  - Forecasting page (historical + generated forecast chart)
  - Risk page (risk table + semantic search)
  - Weather page (live weather pull)
  - Purchase orders / savings placeholders

---

## `docs/`

- `docs/PROJECT_DOCUMENT.md`
  - Day 1 project document (problem, architecture, roles)
- `docs/architecture_diagram.py`
  - architecture image generate karne ka script
- `docs/architecture_diagram.png`
  - generated diagram

---

## `progress/`

- `progress/README.md`
  - overall day-wise tracker
- `progress/day-1/README.md`
- `progress/day-2/README.md`
- `progress/day-3/README.md`
  - completed work documented
- `progress/day-4..day-6`
  - pending plans

---

## Root files

- `README.md` -> public-facing project overview
- `requirements.txt` -> dependencies
- `.env.example` -> sample env template (real secrets nahi)
- `.env` -> local secrets/config (gitignored)
- `.gitignore` -> sensitive/local files ignore

---

## 4) Code flow simple Hinglish me (end-to-end)

1. User Streamlit open karta hai (`frontend/app.py`).
2. Streamlit API call bhejta hai FastAPI backend ko.
3. Router request receive karta hai (example: `/api/v1/inventory`).
4. Router DB session dependency se data fetch karta hai.
5. Response JSON me UI ko jata hai.
6. Forecast generate karte waqt:
   - Sales data DB se load hota hai
   - `forecasting_service.generate_forecast()` run hota hai
   - Prophet available hai to `prophet_v1`, nahi to fallback model
   - Forecast DB table me save hota hai
   - Streamlit confidence interval chart render karta hai
7. Risk search me:
   - startup pe risk events ChromaDB index ho chuke hote hain
   - query hit karti hai `/api/v1/risks/search`
   - semantic similar events return hote hain

---

## 5) Abhi tak ka progress (Day 1 to Day 3)

## Day 1 (Problem & Planning) - Done
- Problem statement clear
- system architecture finalized
- DB schema outline
- FastAPI + Streamlit initialization
- project document + architecture diagram

## Day 2 (Data Integration & Skeleton) - Done
- PostgreSQL (recommended) / SQLite + seed pipeline
- WeatherAPI integration (location input working)
- raw sales/inventory display in dashboard

## Day 3 (Core Forecasting & RAG) - Done
- Prophet forecasting with confidence intervals
- fallback model for stability
- risk RAG with semantic retrieval
- forecast generation API + risk search API

## Day 4 (Agent Orchestration & PO Generation) - Done
- **ROP** (Reorder Point) = avg_daily × lead_time + safety_stock
- **EOQ** (Economic Order Quantity) = √(2 × annual_demand × ordering_cost / holding_cost)
- **Supplier Scoring**: 35% reliability + 35% price efficiency + 30% lead-time efficiency
- **ReAct Agent** banaya jo OpenAI GPT-4o-mini use karta hai chain-of-thought reasoning ke saath
  - 4 tools: check_inventory, get_forecast, search_risks, select_supplier
  - Agent decide karta hai REORDER ya NO_REORDER
  - REORDER hone pe PO auto-draft hota hai DB me
- **Fallback**: Agar OpenAI fail ho → deterministic ROP/EOQ logic use hoti hai
- **Frontend**: Agent Orchestration page — single product run, bulk scan, PO history
- **Prompt Tuning**: Temperature 0.3, supplier scoring weights in prompt, structured DECISION format

---

## 6) Project run karne ke exact steps (till current progress) — PostgreSQL

**Default path:** PostgreSQL + `DATABASE_URL` (project spec / README ke saath align).

### Step 0: PostgreSQL + database banao
- Windows: PostgreSQL install karo (e.g. `winget install PostgreSQL.PostgreSQL.18`) ya [postgresql.org](https://www.postgresql.org/download/windows/) se.
- `psql` PATH me hona chahiye (usually `C:\Program Files\PostgreSQL\<version>\bin`).

**PowerShell example** (password apna lagao):

```powershell
$env:PGPASSWORD = "your_postgres_password"
psql -U postgres -h localhost -p 5432 -d postgres -c "CREATE DATABASE supply_chain;"
```

Agar DB pehle se hai to error aa sakta hai — ignore / skip kar sakte ho.

### Step 1: dependency install
```bash
pip install -r requirements.txt
```
Isme **`psycopg2-binary`** bhi hai taaki PostgreSQL connection chale.

### Step 2: env setup
**Windows:** `Copy-Item .env.example .env`  
**macOS/Linux:** `cp .env.example .env`

Phir `.env` me **ek hi active** `DATABASE_URL` rakho (duplicate lines mat rakho — last line override karti hai):

```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/supply_chain
WEATHERAPI_KEY=<your_weatherapi_key>
```

### Step 3: data load — **PostgreSQL (ya SQLite) me kaun sa data?** ek command choose karo

**Synthetic (project wala dummy / seasonal + risks):**
```bash
python database/load_project_data.py seed
```
Pehle se data hai aur dubara synthetic chahiye → `python database/load_project_data.py seed --replace`

**Kaggle (real Superstore / Online Retail) — same DB, `DATABASE_URL`:**
```bash
pip install kagglehub
python database/load_project_data.py kaggle
python database/load_project_data.py kaggle --preset online-retail --max-products 80
```

**Bas CSV path hai:**
```bash
python database/load_project_data.py csv --path "C:\path\to\file.csv"
```

Kaggle / CSV import **products + sales + inventory** replace karti hai; built-in **risk** rows purane reh sakte hain — full synthetic dubara chahiye ho to `seed --replace`. Detail: `import_kaggle_retail.py` ke top comment me.

### Step 4: backend start
```bash
uvicorn backend.app.main:app --reload --port 8000
```

### Step 5: frontend start
```bash
streamlit run frontend/app.py
```

### Step 6: quick API checks
```bash
curl http://127.0.0.1:8000/health
curl "http://127.0.0.1:8000/api/v1/weather?q=Mumbai"
curl http://127.0.0.1:8000/api/v1/products
```

### Optional: sirf SQLite se jaldi test
Agar PostgreSQL band hai aur quickly dekhna ho:

```env
DATABASE_URL=sqlite:///./supply_chain.db
```

Phir dubara `python database/seed_data.py` chalao. Presentation / viva ke liye **PostgreSQL wala flow** explain karna better hai.

---

## 7) 7-member team role division (students ke hisaab se: kisne kya kiya)

Niche diya gaya split aise बोलो presentation me: “hum 7 members ne parallel kaam divide kiya.”

## Student 1 - Project Coordinator (Day 1 owner)
- Problem statement finalize kiya (5-15% revenue loss framing).
- Architecture flow document me lock kiya.
- `docs/PROJECT_DOCUMENT.md` structure banaya.
- Daily progress tracking `progress/` folder me maintain ki.

## Student 2 - Database & Data Modeling (Day 1 + Day 2 owner)
- `database/schema.sql` design kiya (inventory, sales, PO, risks, forecasts).
- `backend/app/models/schema.py` ORM mapping align ki.
- Data relationships validate kiye (product-supplier, PO-items, etc.).

## Student 3 - Data Simulation & ETL (Day 2 owner)
- `database/seed_data.py` banaya.
- 2+ years realistic daily sales generate kiye with seasonality/noise/promo.
- Risk incidents + supplier data inject kiya for demo realism.

## Student 4 - Backend API Engineer (Day 1 + Day 2 owner)
- FastAPI routers banaye/updated (`inventory`, `forecasting`, `purchase_orders`, `health`, `weather`, `risk`).
- DB session flow stable banaya (sync session local setup).
- Endpoint contracts clear rakhe so frontend directly consume kar sake.

## Student 5 - Forecasting Engineer (Day 3 owner)
- `backend/app/services/forecasting_service.py` implement kiya.
- Prophet logic + confidence interval + fallback model add kiya.
- Forecast generation endpoint ko DB persistence ke saath integrate kiya.

## Student 6 - Risk Intelligence / RAG Engineer (Day 3 owner)
- `backend/app/services/risk_rag_service.py` create kiya.
- ChromaDB indexing + semantic retrieval pipeline add ki.
- `GET /api/v1/risks/search` ko natural-language query capable banaya.

## Student 7 - Frontend + QA + Demo Engineer (Day 1-4 owner)
- `frontend/app.py` me dashboard pages integrate kiye.
- Raw data tables, forecast graphs, risk search UI, weather page connect ki.
- Day 4: Agent Orchestration page — single product run, bulk scan, PO history, tool call log.
- End-to-end smoke tests run kiye; demo flow aur Q/A prep document kiya.

## Day 4 Additions to Team Contributions

- **Student 4** (Backend): `backend/app/routers/agent.py` — agent endpoints (stock-analysis, run, scan, po-history).
- **Student 5** (Forecasting): Forecasting data feeds into agent context for demand-aware reorder decisions.
- **Student 6** (Risk/RAG): Risk intelligence feeds into agent's supply-chain risk assessment before PO drafting.
- **Student 3** (Agent Lead): `backend/app/services/agent_service.py` + `po_generation_service.py` — ReAct agent, ROP/EOQ, supplier scoring, PO creation.

---

## 8) Presentation ke liye teacher Q/A bank (Day 1-3 scope)

## A) Problem & Scope Questions

1. **Q:** Aapne exact business problem kya target kiya?
   **A:** SMBs ka 5-15% revenue inventory mismatch ki wajah se lose hota hai (overstock waste + stockout lost sales).

2. **Q:** LSTM kyun nahi, Prophet kyun?
   **A:** MVP scope me quick interpretability + low-data robustness chahiye thi. Prophet seasonal retail patterns par fast aur stable hai.

3. **Q:** Project ka Day 3 tak boundary kya hai?
   **A:** Day 3 tak data integration, forecasting core, risk retrieval core complete. Autonomous PO agent orchestration Day 4 ka target hai.

## B) Architecture Questions

4. **Q:** Data flow explain karo.
   **A:** DB + external weather data -> forecasting service -> API layer -> Streamlit dashboard.

5. **Q:** RAG kahan fit hota hai architecture me?
   **A:** Risk intelligence lane me. Historical incidents vectorized/indexed hote hain, natural language query se relevant incidents fetch hote hain.

## C) Data Questions

6. **Q:** Real data ya dummy?
   **A:** Day 2 me realistic synthetic data: 2+ years daily series with trend, seasonality, promotions, noise. Isse forecasting behavior realistic banta hai.

7. **Q:** Aapne seasonality kaise simulate ki?
   **A:** Product-wise seasonal peak day + amplitude model kiya gaya; weekend uplift + promo multipliers add kiye.

## D) Forecasting Questions

8. **Q:** Forecast confidence intervals ka use kya?
   **A:** Planning uncertainty show karta hai; reorder decisions me upper/lower bounds risk-adjusted decisions help karte hain.

9. **Q:** Agar Prophet fail ho jaye to?
   **A:** Fallback seasonal-naive model auto use hota hai, pipeline break nahi hota.

10. **Q:** Model output kahan persist hota hai?
    **A:** `demand_forecasts` table me; endpoint se readback hota hai.

## E) API/Engineering Questions

11. **Q:** Aapka backend stateless hai?
    **A:** API stateless request handling karta hai; state DB + vector index me persist hoti hai.

12. **Q:** Weather key secure kaise rakha?
    **A:** `.env` local and gitignored; `.env.example` me placeholder only.

13. **Q:** Database kya use kar rahe ho — PostgreSQL ya SQLite?
    **A:** Design aur demo ke liye **PostgreSQL** (`DATABASE_URL=postgresql://...`). SQLite optional hai quick local test ke liye; `seed_data.py` dono se chal jata hai.

14. **Q:** Testing kaise kiya?
    **A:** Endpoint smoke tests:
    - health
    - products/inventory
    - weather location query
    - forecast generation
    - risk semantic search

## F) RAG Questions

15. **Q:** RAG retrieval quality kaise judge ki?
    **A:** Query-specific top-k relevance check + returned incident text sanity validation.

16. **Q:** Agar Chroma unavailable ho?
    **A:** Service graceful fallback message return karti hai; app crash nahi hota.

## G) Demo Questions

17. **Q:** Live demo me kya flow dikhana hai?
    **A:** Inventory table -> low stock -> forecast generate -> forecast graph -> risk query -> weather signal -> Agent Orchestration -> PO generation.

18. **Q:** Business value abhi tak kya prove hota hai?
    **A:** Data-driven visibility + demand foresight + risk awareness + automated PO drafting, jo stockouts/overstocks reduce karta hai aur procurement speed improve karta hai.

## H) Day 4 Agent & PO Questions

19. **Q:** ROP formula kya hai?
    **A:** ROP = avg_daily_demand × lead_time_days + safety_stock. Jab stock ≤ ROP → reorder trigger.

20. **Q:** EOQ formula kya hai?
    **A:** EOQ = √(2 × annual_demand × ordering_cost / holding_cost_per_unit). Optimal order qty jo total inventory cost minimize karti hai.

21. **Q:** Supplier selection kaise hota hai?
    **A:** Composite score: 35% reliability + 35% price efficiency + 30% lead-time efficiency. Sabse high score wala supplier auto-select hota hai.

22. **Q:** Agent ka chain-of-thought kaise kaam karta hai?
    **A:** OpenAI GPT-4o-mini ko inventory status, forecast, risk alerts, supplier info bhejte hain. Wo step-by-step sochta hai: stock check → demand forecast compare → risk assess → supplier evaluate → REORDER/NO_REORDER decide karta hai with qty.

23. **Q:** Agar OpenAI API fail ho jaye to?
    **A:** Fallback logic activate hoti hai — deterministic ROP/EOQ calculation se decide hota hai reorder karna hai ya nahi. App crash nahi hota.

24. **Q:** Agent kya tools use karta hai?
    **A:** 4 tools: check_inventory (stock + ROP/EOQ), get_forecast (Prophet summary), search_risks (ChromaDB semantic search), select_supplier (composite scoring).

25. **Q:** PO automatically kaise create hota hai?
    **A:** Agent REORDER decide kare → best supplier select → PurchaseOrder + PurchaseOrderItem records DB me insert. Status "draft" hoti hai review ke liye.

26. **Q:** Prompt tuning kya kiya?
    **A:** (a) Temperature 0.3 for consistent decisions, (b) supplier scoring formula explicitly prompt me, (c) structured DECISION format for reliable parsing, (d) risk context added so agent delays consider karta hai.

---

## 9) Presentation script (quick speaking order for 7 members)

1. Member 1: Problem + scope (1 min)  
2. Member 2: Data model + schema + seeding (2 min)  
3. Member 4: API architecture + endpoints (2 min)  
4. Member 6: Streamlit walkthrough (2 min)  
5. Member 3: Forecast model logic + intervals (2 min)  
6. Member 5: RAG risk search + Agent Orchestration demo (2 min)  
7. Member 7: PO generation, testing, fallback strategy (1-2 min)

---

## 10) Important notes for viva

- Day 4 tak project ko "end-to-end pipeline complete" bol sakte ho — data se PO tak autonomous flow hai.
- Prophet + RAG + ReAct agent dono ka rationale clear rakhna.
- "Why this architecture?" ka crisp answer: modular, testable, and demo-friendly.
- Secret management best practice mention karna (no keys in public repo).
- Agent fallback mention karna — OpenAI down hone pe bhi system kaam karta hai.

---

## 11) Next planned (Day 5+ preview)

- Dashboard polish + Plotly charts for stock/forecast/risk
- automated PO draft generation with ROP/EOQ reasoning
- richer dashboard polish + savings report
- final demo + Q&A defense packaging

