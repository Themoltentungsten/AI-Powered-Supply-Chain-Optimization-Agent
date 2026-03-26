# AI-Powered Supply Chain Optimization Agent

## Project Report

---

# 1. Title Page

**Project Title:** AI-Powered Supply Chain Optimization Agent

**Submitted by:**
- [Student Name 1] — Roll No. [XXXX]
- [Student Name 2] — Roll No. [XXXX]
- [Student Name 3] — Roll No. [XXXX]
- [Student Name 4] — Roll No. [XXXX]

**Under the Guidance of:**  
Prof. [Faculty Name]  
Department of Computer Science & Engineering

**College:** [College Name]  
**University:** [University Name]  
**Course:** B.Tech — Computer Science & Engineering (Data Science)  
**Academic Year:** 2025–2026  
**Submission Date:** March 2026

---

# 2. Certificate

## Certificate

This is to certify that the project entitled **"AI-Powered Supply Chain Optimization Agent"** is a bonafide record of work carried out by the following students:

| Name | Roll Number |
|------|-------------|
| [Student Name 1] | [XXXX] |
| [Student Name 2] | [XXXX] |
| [Student Name 3] | [XXXX] |
| [Student Name 4] | [XXXX] |

in partial fulfillment of the requirements for the award of the degree of **Bachelor of Technology in Computer Science & Engineering (Data Science)** during the academic year **2025–2026** at **[College Name]**.

This project has been completed under my guidance and supervision and is approved for submission.

&nbsp;

**Project Guide:**  
Prof. [Faculty Name]  
Department of CSE  
Date: ___________  

&nbsp;

**Head of Department:**  
Prof. [HOD Name]  
Department of CSE  
Date: ___________  

&nbsp;

**External Examiner:**  
Name & Signature  
Date: ___________

---

# 3. Acknowledgement

We would like to express our sincere gratitude to our project guide, **Prof. [Faculty Name]**, for their invaluable guidance, constant encouragement, and constructive feedback throughout the development of this project. Their expertise in artificial intelligence and data science was instrumental in shaping the direction of this work.

We are grateful to the **Head of the Department, Prof. [HOD Name]**, and the entire faculty of the Department of Computer Science & Engineering for providing us with the necessary resources, laboratory facilities, and academic environment to carry out this project.

We extend our thanks to **[College Name]** for providing the infrastructure and computing resources required for developing and testing the system.

We also acknowledge the open-source community for providing excellent tools and libraries — including Python, FastAPI, Streamlit, Prophet, LangChain, ChromaDB, and PostgreSQL — that made this project technically feasible.

Finally, we thank our families and friends for their unwavering support and encouragement throughout this academic journey.

---

# 4. Abstract

Small and medium businesses (SMBs) lose an estimated **5–15% of annual revenue** due to inventory mismanagement. Overstocking leads to waste and increased holding costs, while stockouts result in lost sales and customer dissatisfaction. Traditional inventory management relies on manual processes and static reorder rules that fail to account for demand variability, seasonal trends, and external disruptions.

This project presents an **AI-Powered Supply Chain Optimization Agent** that addresses these challenges through a multi-layered intelligent system. The system integrates:

- **Prophet-based demand forecasting** to predict future demand with confidence intervals, accounting for yearly and weekly seasonality patterns.
- **A ReAct (Reasoning + Acting) agent** powered by OpenAI GPT-4o-mini that autonomously monitors inventory levels, interprets forecasts, assesses supply chain risks, evaluates live weather conditions, scores suppliers, and generates purchase orders.
- **Retrieval-Augmented Generation (RAG)** using ChromaDB to semantically search and retrieve relevant supply chain risk events, providing the agent with contextual intelligence.
- **An interactive Streamlit dashboard** with Plotly-powered charts for real-time visualization of inventory health, demand forecasts, risk alerts, stockout predictions, and projected monthly savings.

The system demonstrates end-to-end automation of the supply chain planning cycle: from data ingestion and demand prediction to autonomous procurement decision-making and stakeholder reporting. Testing with both synthetic seasonal data and agriculture-specific datasets (15 crop products with varied stock levels) shows the system can identify stockout risks days in advance, draft optimized purchase orders balancing cost, reliability, and delivery speed, and project monthly savings from reduced waste and prevented lost sales.

**Keywords:** Supply Chain Optimization, Demand Forecasting, Prophet, LangChain, ReAct Agent, RAG, Purchase Order Automation, Streamlit Dashboard

---

# 5. Table of Contents

| Section | Title | Page |
|---------|-------|------|
| 1 | Title Page | 1 |
| 2 | Certificate | 2 |
| 3 | Acknowledgement | 3 |
| 4 | Abstract | 4 |
| 5 | Table of Contents | 5 |
| 6 | Introduction | 6 |
| 7 | Problem Statement | 8 |
| 8 | Objectives | 9 |
| 9 | Scope of the Project | 10 |
| 10 | System Architecture | 11 |
| 11 | Methodology | 13 |
| 12 | Technologies Used | 15 |
| 13 | Implementation Details | 16 |
| 14 | Key Features | 18 |
| 15 | Results & Output | 19 |
| 16 | Advantages | 21 |
| 17 | Limitations | 22 |
| 18 | Future Enhancements | 23 |
| 19 | Conclusion | 24 |

---

# 6. Introduction

## 6.1 Background of Supply Chain Management

Supply chain management (SCM) encompasses the planning, execution, and monitoring of all activities involved in sourcing, procurement, conversion, and logistics management. In modern business, supply chains have evolved from simple linear processes into complex, interconnected networks spanning multiple geographies, suppliers, warehouses, and distribution channels.

For small and medium businesses (SMBs), effective supply chain management is particularly critical. Unlike large enterprises with dedicated procurement teams and enterprise resource planning (ERP) systems costing millions of dollars, SMBs often rely on manual processes, spreadsheets, and intuition-based ordering. This approach becomes increasingly untenable as product catalogs grow, demand patterns become more complex, and global supply chain disruptions become more frequent.

## 6.2 Growing Complexity in Modern Supply Chains

Several factors have amplified supply chain complexity in recent years:

- **Demand volatility:** Consumer preferences shift rapidly, influenced by social media trends, seasonal patterns, and economic conditions. Traditional static reorder rules cannot adapt to these fluctuations.
- **Global supply disruptions:** Events such as pandemics, port congestion, geopolitical tensions, and climate change have made supply chains more fragile. A supplier delay in one region can cascade across the entire chain.
- **Perishable goods management:** Industries like agriculture and food retail face additional challenges — products have limited shelf life, and weather directly impacts both supply (crop yield) and demand (consumer purchasing behavior).
- **Information overload:** Businesses now have access to vast amounts of data — point-of-sale transactions, weather feeds, news reports, supplier performance metrics — but lack the tools to synthesize this information into actionable decisions.

## 6.3 Role of Artificial Intelligence in Supply Chain Optimization

Artificial intelligence (AI) and machine learning (ML) offer transformative potential for supply chain management:

- **Demand Forecasting:** Time-series models like Prophet and LSTM can detect seasonal patterns, trend changes, and anomalies in historical sales data to predict future demand with quantified uncertainty.
- **Autonomous Decision-Making:** AI agents can continuously monitor inventory levels, evaluate multiple data sources (forecasts, weather, risk intelligence), and take procurement actions without human intervention.
- **Risk Intelligence:** Natural language processing (NLP) and vector databases enable semantic search over unstructured risk data, allowing systems to identify relevant threats from historical incidents.
- **Real-Time Dashboards:** Interactive visualization tools provide stakeholders with immediate visibility into inventory health, demand trends, and cost optimization opportunities.

## 6.4 Project Overview

This project implements an **AI-Powered Supply Chain Optimization Agent** that combines these AI capabilities into a unified, end-to-end system. The system ingests historical sales data, generates demand forecasts using Meta's Prophet model, employs a ReAct (Reasoning + Acting) agent backed by OpenAI's GPT-4o-mini for autonomous purchase order generation, uses RAG (Retrieval-Augmented Generation) over ChromaDB for risk intelligence, integrates live weather data as an external signal, and presents all insights through an interactive Streamlit dashboard.

The project is designed as a practical demonstration of how modern AI technologies can be composed to solve a real-world business problem — transforming reactive, manual inventory management into proactive, data-driven supply chain optimization.

---

# 7. Problem Statement

Small and medium businesses (SMBs) in retail and agriculture sectors face significant revenue loss due to inefficient inventory management. The core problems are:

### 7.1 Stockouts

When inventory runs out before new stock arrives, businesses lose immediate sales revenue and long-term customer loyalty. Studies estimate that stockouts cost retailers **4–8% of annual sales**. For agricultural products, stockouts during peak harvest seasons can mean losing an entire seasonal demand window.

### 7.2 Overstocking

Excessive inventory ties up working capital and incurs holding costs (warehousing, insurance, depreciation). For perishable goods like fruits, vegetables, and dairy, overstocking leads directly to waste — the USDA estimates that **30–40% of the food supply in the United States is wasted**, much of it due to poor demand planning.

### 7.3 Manual Reordering Processes

Most SMBs determine reorder quantities using fixed rules (e.g., "order 100 units when stock drops below 50") that do not account for:

- Seasonal demand variations (e.g., higher rice demand during festivals)
- External factors (e.g., weather-driven demand spikes for beverages)
- Supply-side risks (e.g., port delays, supplier unreliability)
- Changing consumer patterns over time

### 7.4 Lack of Data-Driven Decision Making

While SMBs collect point-of-sale data, they rarely use it for predictive analytics. Decisions are based on intuition or lagging indicators rather than forward-looking forecasts. Risk events (supplier delays, regional disruptions) are tracked informally, if at all.

### 7.5 Problem Summary

The project addresses the following composite problem:

> **How can SMBs leverage AI to automatically forecast demand, assess supply chain risks, and generate optimized purchase orders — reducing both waste from overstocking and lost sales from stockouts — without requiring dedicated data science expertise?**

---

# 8. Objectives

The primary objectives of this project are:

1. **Demand Forecasting:** Implement a time-series forecasting engine using Meta's Prophet model to predict future demand for each product, accounting for yearly and weekly seasonality, with quantified confidence intervals.

2. **Inventory Monitoring:** Develop an automated system that continuously monitors inventory levels against calculated Reorder Points (ROP) and Economic Order Quantities (EOQ), flagging products that require restocking.

3. **Autonomous Purchase Order Generation:** Build a ReAct (Reasoning + Acting) AI agent that synthesizes inventory status, demand forecasts, weather conditions, and risk intelligence to autonomously draft purchase orders with clear chain-of-thought justification.

4. **Supply Chain Risk Intelligence:** Implement a Retrieval-Augmented Generation (RAG) pipeline using ChromaDB to semantically search historical risk events and surface relevant threats for the agent's decision-making process.

5. **Weather-Aware Decisions:** Integrate live weather data to enable the agent to factor extreme weather conditions (drought, storms, floods, heatwaves) into its reorder urgency and quantity calculations, particularly for agricultural and perishable products.

6. **Interactive Dashboard:** Build a visually polished Streamlit dashboard with Plotly charts that provides real-time visibility into inventory health, demand forecasts, risk alerts, stockout predictions, and projected monthly cost savings.

7. **Cost Optimization:** Demonstrate projected monthly savings from reduced overstock holding costs and prevented stockout losses, framing the agent as a business cost-saver.

8. **Supplier Optimization:** Implement a multi-criteria supplier scoring algorithm that balances price competitiveness (35%), delivery reliability (35%), and lead-time efficiency (30%) to select the optimal supplier for each purchase order.

---

# 9. Scope of the Project

## 9.1 In-Scope (MVP)

The minimum viable product (MVP) of this project includes:

- **Prophet-based demand forecasting** with yearly and weekly seasonality detection, multiplicative seasonality mode, and seasonal-naive fallback for products with insufficient data.
- **ReAct agent orchestration** using OpenAI GPT-4o-mini with five tools: check inventory, get forecast, get weather, search risks, and select supplier.
- **Automated purchase order generation** with status tracking (draft, submitted, approved, received).
- **RAG-based risk analysis** using ChromaDB vector database for semantic search over supply chain risk events.
- **Interactive Streamlit dashboard** with nine pages: Dashboard, Inventory, Demand Forecasting, Purchase Orders, Risk Alerts, Weather, Agent Orchestration, Data Manager, and Savings Report.
- **Multiple data sources:** Synthetic seasonal data generator, agriculture/farming dataset (15 crops), Kaggle CSV import, and kagglehub preset integration.
- **PostgreSQL database** with 10+ tables for products, suppliers, inventory, sales history, forecasts, purchase orders, risk events, weather data, and data source management.

## 9.2 Design Decisions

- **Prophet over LSTM:** Prophet was chosen over LSTM/deep learning models because it handles seasonality natively, works effectively with as little as one year of daily data, automatically detects trend changes, and requires no manual feature engineering. LSTM would require significantly more data and hyperparameter tuning for comparable seasonal pattern detection.
- **ReAct over Simple Rule Engine:** The ReAct pattern was chosen because it allows the agent to reason dynamically about novel situations (e.g., unusual weather + risk combinations) rather than following rigid if-then rules.
- **ChromaDB over Traditional Search:** Vector-based semantic search allows natural language queries (e.g., "drought affecting grain supply") rather than requiring exact keyword matches.

## 9.3 Out-of-Scope

The following are recognized as future enhancements beyond the current MVP:

- Real-time ERP integration (SAP, Oracle)
- LSTM/Transformer-based forecasting models
- Multi-warehouse inventory optimization
- Automated supplier communication (email/API)
- Mobile application for warehouse managers
- Multi-agent collaboration systems

---

# 10. System Architecture

## 10.1 High-Level Architecture

The system follows a four-layer architecture:

```
Data Integration Layer → Demand Forecasting Engine → AI Agent Orchestration → Interactive Dashboard
```

Each layer builds upon the previous one, creating a pipeline that transforms raw data into actionable procurement decisions.

## 10.2 Architecture Diagram Description

The system architecture can be visualized as a flow diagram with the following components and connections:

**Data Sources (Left)**
- PostgreSQL Database (products, inventory, sales history, suppliers, risk events)
- WeatherAPI.com (live weather feed)
- Kaggle / CSV data imports

**Backend Layer (Center-Left)**
- FastAPI REST API with modular routers
- SQLAlchemy ORM for database operations
- Data validation and transformation

**Processing Layer (Center)**
- Prophet Forecasting Engine (time-series predictions)
- ChromaDB RAG Pipeline (risk event vector search)
- ROP/EOQ Calculator (inventory mathematics)
- Supplier Scoring Engine (multi-criteria optimization)

**Agent Layer (Center-Right)**
- ReAct Agent Orchestrator
- OpenAI GPT-4o-mini (chain-of-thought reasoning)
- Tool execution loop (5 tools: inventory, forecast, weather, risks, supplier)
- PO Generation Module

**Presentation Layer (Right)**
- Streamlit Frontend (9 pages)
- Plotly Interactive Charts
- Real-time KPI metrics and alerts

**Arrows show data flow:**
- Data sources → FastAPI → Processing engines
- Processing engines → Agent (via tool calls)
- Agent → PO database write
- All layers → Streamlit dashboard

## 10.3 Component Details

### PostgreSQL Database
The database stores all persistent state: product catalog, current inventory levels, historical sales transactions, supplier information, demand forecasts, purchase orders, risk events, and weather data. SQLAlchemy ORM provides type-safe, Pythonic access to all tables.

### FastAPI Backend
The REST API layer exposes 15+ endpoints organized into modular routers (health, inventory, forecasting, purchase orders, weather, risks, agent, data management, savings). Each router handles its domain's CRUD operations and business logic.

### Prophet Forecasting Engine
Meta's Prophet model is configured with multiplicative seasonality mode to capture percentage-based demand variations. The engine auto-generates forecasts for products when the agent requests them, storing results in the database for dashboard visualization.

### ChromaDB RAG Pipeline
Risk events are embedded as vectors using ChromaDB's default embedding model. When the agent needs risk intelligence for a product category, it performs semantic search to find the most relevant historical risk events, which are included in the agent's reasoning context.

### ReAct Agent
The agent follows the Reasoning + Acting paradigm: it receives a task (evaluate a product for reorder), calls tools iteratively to gather context (inventory → forecast → weather → risks → supplier), then synthesizes all information into a structured decision with full chain-of-thought reasoning.

### Streamlit Dashboard
The frontend provides nine specialized pages, each focused on a specific aspect of supply chain monitoring: real-time inventory overview, demand forecasting with confidence intervals, agent orchestration with visible reasoning chains, and monthly savings projections.

---

# 11. Methodology

## 11.1 Data Collection and Preparation

The system supports three data ingestion methods:

**Synthetic Data Generation:** A Python script generates realistic seasonal sales data for a configurable set of products. Each product has a base demand level, seasonal amplitude, and peak day parameter that create smooth sinusoidal demand patterns with random noise. This produces 365 days of daily sales history per product, enabling Prophet to detect seasonal patterns.

**Agriculture/Farming Dataset:** A specialized dataset generator creates 15 crop products (rice, wheat, corn, tomatoes, mangoes, cotton, coffee, etc.) with deliberately varied stock levels: some above the reorder point (healthy), some below the reorder point (needing reorder), and some below safety stock (critical). This dataset also includes 10 agriculture-specific risk events (drought, pest outbreak, monsoon flooding, heatwave, export ban, etc.) and 8 agricultural suppliers. This mixed-scenario dataset is designed to demonstrate the agent's decision-making across different urgency levels.

**Kaggle Import:** The system can import real-world retail datasets from Kaggle (Superstore Sales, Online Retail) via CSV upload or the kagglehub API. An intelligent column detection system maps various CSV schemas to the internal product/sales data model.

## 11.2 Demand Forecasting with Prophet

The forecasting pipeline follows these steps:

1. **Data Aggregation:** Daily sales records are summed per product to create a time series with columns `ds` (date) and `y` (quantity sold).

2. **Model Configuration:** Prophet is initialized with multiplicative seasonality mode, which models seasonal effects as percentage multipliers rather than additive offsets. This is more appropriate for retail and agricultural demand where seasonal variation scales with the base demand level.

3. **Training:** The model fits on available historical data (minimum 30 days required). Prophet automatically detects yearly and weekly seasonality components.

4. **Prediction:** The model generates forecasts for a configurable horizon (7–90 days), producing point predictions (`yhat`), lower bounds (`yhat_lower`), and upper bounds (`yhat_upper`) that define an 80% confidence interval.

5. **Storage:** Forecast results are persisted in the `demand_forecasts` table for dashboard visualization and agent consumption.

6. **Fallback:** If Prophet fails to converge (e.g., insufficient data or numerical issues), the system falls back to a seasonal-naive model using NumPy that repeats the most recent weekly pattern.

## 11.3 RAG-Based Risk Analysis

The risk analysis module implements Retrieval-Augmented Generation (RAG):

1. **Indexing:** Risk events from the database (event type, severity, description, affected suppliers, affected region) are formatted as text documents and inserted into a ChromaDB collection as vector embeddings.

2. **Semantic Search:** When queried (either by the agent or through the dashboard's search interface), the system performs a nearest-neighbor search in embedding space to find risk events semantically relevant to the query, even if they don't share exact keywords.

3. **Relevance Scoring:** Results include a relevance score (cosine similarity) that indicates how closely each risk event matches the query context.

4. **Agent Integration:** The agent calls the `search_risks` tool with a description of the product and its supply chain context. The returned risk events inform the agent's assessment of supply chain vulnerability and reorder urgency.

## 11.4 Agent Decision Logic

The ReAct agent follows a structured decision process:

**Step 1 — Inventory Assessment:**
The agent queries current stock levels and calculates:
- **Reorder Point (ROP):** ROP = average_daily_demand × lead_time_days + safety_stock
- **Economic Order Quantity (EOQ):** EOQ = √(2 × annual_demand × ordering_cost / holding_cost_per_unit)

**Step 2 — Demand Forecast Review:**
The agent retrieves (or auto-generates) a 30-day demand forecast, examining total predicted demand and average daily demand rate.

**Step 3 — Weather Assessment:**
Live weather data is fetched for the specified location. The agent evaluates whether conditions (temperature extremes, heavy precipitation, storms) could affect supply chains or demand patterns.

**Step 4 — Risk Intelligence:**
The agent searches ChromaDB for risk events relevant to the product's category and supply chain context, identifying active threats (droughts, pest outbreaks, port delays, supplier issues).

**Step 5 — Supplier Selection:**
The agent scores available suppliers using a weighted composite formula:
- Reliability score: 35% weight
- Price competitiveness: 35% weight (inverted, so lower price = higher score)
- Lead-time efficiency: 30% weight (inverted, so shorter lead time = higher score)

**Step 6 — Decision:**
The agent synthesizes all context into a chain-of-thought reasoning narrative and outputs a structured decision:
- `DECISION: REORDER <quantity>` — with the chosen supplier and justification
- `DECISION: NO_REORDER` — with explanation of why current stock is sufficient

**Step 7 — PO Generation:**
If the decision is REORDER, the system automatically creates a purchase order record in the database with status "draft," linked to the selected supplier, with the agent's full reasoning stored for audit purposes.

## 11.5 Weather Integration

The system integrates live weather data from WeatherAPI.com:

- Current temperature, humidity, precipitation, wind speed, and condition description are fetched for a configurable location.
- The agent's system prompt instructs it to consider extreme weather as a risk factor: droughts can disrupt crop supply, storms can delay transportation, and heatwaves can spike demand for certain products.
- For agricultural products, weather is treated as a critical decision factor — the agent may increase order quantities beyond the standard EOQ when extreme weather threatens supply.

## 11.6 Savings Analysis

The savings module calculates projected monthly cost optimization:

- **Overstock holding cost:** For products above the reorder point, excess inventory × unit cost × 20% annual carrying rate, prorated monthly.
- **Stockout lost sales:** For products below the reorder point, the deficit × selling price × 50% estimated lost-sale probability.
- **Total potential savings:** The sum of overstock waste and stockout losses that the agent's automated reordering can eliminate.

---

# 12. Technologies Used

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.12 | Core programming language for backend, frontend, and data processing |
| FastAPI | 0.115+ | Asynchronous REST API framework with automatic OpenAPI documentation |
| Streamlit | 1.40+ | Interactive web-based dashboard framework for data visualization |
| PostgreSQL | 15+ | Enterprise-grade relational database for persistent data storage |
| SQLAlchemy | 2.0+ | Object-Relational Mapping (ORM) for type-safe database operations |
| Prophet | 1.1+ | Meta's time-series forecasting library with automatic seasonality detection |
| ChromaDB | 0.5+ | Vector database for embedding-based semantic search (RAG pipeline) |
| LangChain | 0.3+ | Framework for developing LLM-powered applications and agent orchestration |
| OpenAI GPT-4o-mini | — | Large language model for chain-of-thought reasoning and decision-making |
| WeatherAPI.com | — | External REST API for real-time weather data |
| Plotly | 5.24+ | Interactive charting library for data visualization in Streamlit |
| Pandas | 2.2+ | Data manipulation and analysis library |
| NumPy | 1.26+ | Numerical computing library (seasonal-naive forecast fallback) |
| Pydantic | 2.0+ | Data validation and settings management via BaseSettings |
| httpx | 0.28+ | Modern HTTP client for external API calls |
| Uvicorn | 0.34+ | ASGI web server for running FastAPI applications |

---

# 13. Implementation Details

## 13.1 Database Schema

The PostgreSQL database consists of the following tables:

**Products Table:** Stores the product catalog with fields for SKU, name, category, unit cost, selling price, unit of measure, lead time in days, and active status. Each product has a unique SKU identifier.

**Suppliers Table:** Contains supplier information including name, contact details, average lead time, reliability score (0–1 scale), and price rating. Suppliers are rated on multiple dimensions for the scoring algorithm.

**Product-Supplier Association Table:** A many-to-many relationship table linking products to their available suppliers with per-product unit prices, enabling different pricing for different products from the same supplier.

**Inventory Table:** Tracks current stock levels for each product with fields for quantity on hand, reorder point, safety stock level, last restocked date, and warehouse location. Each product has exactly one inventory record.

**Sales History Table:** Records daily sales transactions with product ID, sale date, quantity sold, and unit price at time of sale. This is the primary input for demand forecasting.

**Purchase Orders Table:** Stores purchase orders with order date, status (draft/submitted/approved/received), supplier reference, total amount, expected delivery date, actual delivery date, generated-by field (agent or manual), and agent reasoning text.

**Purchase Order Items Table:** Line items for each purchase order containing product reference, quantity ordered, and unit price.

**Risk Events Table:** Supply chain risk events with event date, event type (e.g., port_delay, weather_disruption, supplier_bankruptcy), severity level, description, affected suppliers, and affected region.

**Weather Data Table:** Cached weather observations with location, temperature, humidity, wind speed, precipitation, condition, and observation timestamp.

**Demand Forecasts Table:** Stored forecast results with product reference, forecast date, predicted demand value, lower and upper confidence bounds, and model name used for generation.

**Data Sources Table:** Metadata tracking which datasets have been loaded (synthetic, farming, Kaggle CSV, kagglehub), their activation status, and record counts.

## 13.2 Forecast Generation Pipeline

The forecast generation process is triggered via the API endpoint `POST /forecasts/generate/{product_id}`:

1. Historical sales data is queried from the database and aggregated into daily totals.
2. If fewer than 30 data points exist, the system returns an error with guidance.
3. A Prophet model is instantiated with multiplicative seasonality and yearly/weekly seasonality components.
4. The model is fitted on historical data and used to predict for the requested horizon.
5. Predictions are clipped to ensure non-negative values (demand cannot be negative).
6. Results are stored in the `demand_forecasts` table, replacing any previous forecasts for the same product.
7. If Prophet fails (convergence issues, data problems), the seasonal-naive fallback generates a simple repeating weekly pattern based on recent data.

## 13.3 ROP and EOQ Calculations

**Reorder Point (ROP):**
```
ROP = avg_daily_demand × lead_time_days + safety_stock
```
Where:
- `avg_daily_demand` is computed from the last 90 days of sales history
- `lead_time_days` comes from the product's configured supplier lead time
- `safety_stock` is pre-configured per product (typically 20–50% of ROP)

The ROP represents the inventory level at which a new order should be placed to avoid stockout during the lead time.

**Economic Order Quantity (EOQ):**
```
EOQ = √(2 × annual_demand × ordering_cost / holding_cost_per_unit)
```
Where:
- `annual_demand` = avg_daily_demand × 365
- `ordering_cost` is fixed at a default per-order cost
- `holding_cost_per_unit` = unit_cost × 20% annual carrying rate

The EOQ minimizes total inventory cost by balancing ordering frequency against holding costs.

## 13.4 Purchase Order Automation

When the agent decides to reorder:

1. The supplier scoring algorithm evaluates all active suppliers for the product.
2. Each supplier receives a composite score: 0.35 × reliability + 0.35 × (1 – normalized_price) + 0.30 × (1 – normalized_lead_time).
3. The highest-scoring supplier is selected.
4. A purchase order record is created with status "draft," linking to the chosen supplier.
5. Purchase order items are created with the calculated quantity and current unit price.
6. The expected delivery date is computed as today + supplier's average lead time.
7. The agent's full chain-of-thought reasoning is stored in the PO record for audit and transparency.

## 13.5 Dashboard Pages

The Streamlit frontend consists of nine specialized pages:

1. **Dashboard:** Real-time KPI cards, inventory bar chart with ROP/safety lines, stockout prediction timeline, and active risk alerts.
2. **Inventory:** Full inventory table with color-coded rows for products below reorder point.
3. **Demand Forecasting:** Product selector, historical sales chart, forecast generator, and Prophet prediction with confidence interval shading.
4. **Purchase Orders:** PO listing with KPI summary (total POs, agent-generated, total value).
5. **Risk Alerts:** Risk events table, severity distribution pie chart, and RAG semantic search interface.
6. **Weather:** Live weather fetcher showing temperature, humidity, precipitation, and wind for any location.
7. **Agent Orchestration:** Single-product agent runs with full reasoning display, bulk scan for all low-stock products, and PO history with stored reasoning.
8. **Data Manager:** Four data loading options (synthetic, farming, CSV upload, Kaggle preset), data source switching, and deletion controls.
9. **Savings Report:** Monthly savings projections with cost breakdown charts, per-product analysis table, and business impact narrative.

---

# 14. Key Features

## 14.1 Prophet-Based Demand Forecasting
The system uses Meta's Prophet model with multiplicative seasonality to generate demand predictions with confidence intervals for each product. The model automatically detects yearly and weekly seasonal patterns, enabling accurate forecasting even with limited historical data (as few as 30 daily observations). A seasonal-naive fallback ensures forecasts are always available.

## 14.2 Automated Purchase Order Generation
The ReAct agent autonomously monitors inventory levels against calculated ROP thresholds and generates purchase orders when restocking is needed. Each PO includes the optimal supplier (selected via multi-criteria scoring), the recommended quantity (based on EOQ calculations), expected delivery date, and total cost. The agent's full reasoning chain is preserved for transparency.

## 14.3 RAG-Based Risk Identification
Supply chain risk events are indexed in ChromaDB as vector embeddings, enabling natural language semantic search. Users can query "drought affecting grain supply" and retrieve relevant historical incidents even without exact keyword matches. The agent automatically searches risks during its decision process.

## 14.4 Weather-Aware Supply Chain Decisions
Live weather data from WeatherAPI.com is integrated into the agent's decision context. For agricultural and perishable products, extreme weather (drought, storms, floods, heatwaves) triggers increased urgency and potentially larger order quantities to buffer against supply disruptions.

## 14.5 Real-Time Inventory Monitoring with Stockout Predictions
The dashboard calculates and displays predicted stockout dates for every product based on current stock levels and average daily demand rates. Products are classified as "critical" (< 7 days), "warning" (< 14 days), or "healthy," with color-coded visualizations for immediate identification.

## 14.6 Multi-Source Data Management
The system supports four data ingestion methods: synthetic seasonal data generation, agriculture/farming dataset with mixed stock levels, Kaggle CSV upload with automatic column detection, and kagglehub preset downloads. Users can switch between loaded datasets and view statistics for each.

## 14.7 Monthly Savings Projection
The savings report quantifies the business impact of AI-driven optimization by calculating overstock holding costs (capital tied up in excess inventory) and stockout lost-sale estimates (revenue lost when products are unavailable). The projected monthly savings represent the total optimization potential.

## 14.8 Supplier Scoring and Selection
A multi-criteria optimization algorithm scores suppliers on three dimensions: delivery reliability (35% weight), price competitiveness (35% weight), and lead-time efficiency (30% weight). This composite scoring ensures balanced supplier selection that doesn't optimize for price alone at the expense of delivery reliability.

---

# 15. Results and Output

## 15.1 Dashboard Overview

The main dashboard presents five key performance indicator (KPI) cards at the top of the screen: Total Products, Low Stock Alerts, Total Units in Stock, Reorder Rate (percentage of products below ROP), and Critical Stockout Count. Below the KPIs, an interactive Plotly bar chart displays current stock levels for each product, with bars colored red for products below the reorder point and blue for healthy products. Overlaid line traces show the Reorder Point (dashed red) and Safety Stock (dotted amber) thresholds for comparison.

A second chart — the Stockout Prediction Timeline — shows horizontal bars representing the estimated days of stock remaining for each product. Horizontal reference lines at 7 days (critical threshold) and 14 days (warning threshold) provide immediate visual classification. Products are sorted by urgency, with the most critical appearing first.

The bottom section displays the five most recent risk alerts with severity icons and descriptions, providing at-a-glance risk awareness.

## 15.2 Demand Forecast Output

The demand forecasting page shows a historical sales line chart in gray, transitioning into a Prophet forecast line in blue. The forecast is surrounded by a shaded confidence band (lighter blue) representing the 80% prediction interval. This visualization allows users to see both the predicted demand trajectory and the range of uncertainty.

For a crop like "Basmati Rice" with harvest-season peaks, the forecast clearly shows elevated demand around the peak day (day 300 in the sinusoidal pattern), demonstrating Prophet's ability to capture seasonal patterns from historical data.

## 15.3 Agent Reasoning Output

When the agent is run for a product (e.g., "Corn / Maize" with stock below safety level), the output displays:

- **Decision Banner:** A prominent red banner stating "REORDER — Quantity: 400"
- **Weather Context:** The agent's weather data (e.g., Mumbai: 32°C, 78% humidity, Partly Cloudy)
- **Forecast Context:** Total predicted 30-day demand, model used (Prophet), average daily demand rate
- **Chain-of-Thought Reasoning:** A multi-paragraph narrative explaining:
  - Current inventory status (50 units on hand vs. ROP of 185)
  - Forecast interpretation (30-day demand of 600 units)
  - Weather impact assessment (high temperatures may affect crop storage)
  - Risk factors (drought alert and pest outbreak in ChromaDB results)
  - Supplier selection rationale (AgriGlobal scored highest at 0.823 composite)
  - Final recommendation with quantity justification
- **Purchase Order Details:** PO number, supplier name, quantity, unit price, total cost, expected delivery date

## 15.4 Savings Report Output

The savings report displays eight KPI cards: Total Potential Monthly Savings, Overstock Holding Cost, Stockout Lost Sales Estimate, Agent POs Created, Agent PO Value, Critical Products, Warning Products, and Healthy Products.

Two charts provide visual breakdown:
- A donut chart splitting total costs into Overstock Waste (amber) and Lost Sales (red)
- A bar chart showing the top 10 products by savings potential, color-coded by risk level

A detailed table lists every product with its current stock, reorder point, average daily demand, days of stock remaining, predicted stockout date, risk classification, and individual savings potential.

The page concludes with a business impact narrative stating the total monthly savings figure and breaking it into waste reduction and lost-sales prevention components.

## 15.5 Full Scan Output

The bulk scan feature processes all products below their reorder point in sequence. Results show summary metrics (total scanned, reorders created, no-reorder decisions, errors) and expandable cards for each product showing the agent's decision and reasoning. Products requiring reorder display with red indicators, while healthy products show green.

---

# 16. Advantages

## 16.1 Reduced Manual Effort
The system automates the entire demand planning and procurement cycle — from forecasting to purchase order generation — eliminating the need for manual inventory checks, spreadsheet analysis, and supplier communication. This frees staff to focus on strategic tasks rather than routine monitoring.

## 16.2 Data-Driven Decisions
Every reorder decision is backed by quantitative analysis: historical demand patterns, statistical forecasts with confidence intervals, supplier performance metrics, and risk intelligence. This replaces intuition-based ordering with evidence-based procurement.

## 16.3 Proactive Rather Than Reactive
Traditional inventory management reacts to stockouts after they occur. This system predicts stockouts days or weeks in advance and initiates procurement before stock runs out, preventing lost sales and customer dissatisfaction.

## 16.4 Continuous Autonomous Operation
The AI agent can be configured to run periodic scans (e.g., daily) that automatically evaluate all products and generate purchase orders as needed. This provides 24/7 inventory monitoring without human intervention.

## 16.5 Weather and Risk Awareness
By incorporating live weather data and historical risk intelligence into its decisions, the agent makes more nuanced choices than simple threshold-based rules. For agricultural products, this weather-awareness is particularly valuable — the system can increase order quantities when weather threatens supply disruption.

## 16.6 Transparent Decision-Making
The agent's full chain-of-thought reasoning is stored with every purchase order, providing complete auditability. Stakeholders can review why each order was placed, what factors influenced the decision, and how alternatives were evaluated.

## 16.7 Cost Optimization
The EOQ formula minimizes total inventory cost by balancing ordering frequency against holding costs. Combined with supplier scoring and demand-driven reordering, the system targets a projected 15–25% reduction in inventory-related costs.

## 16.8 Modular and Extensible Architecture
The system's component-based design (separate services for forecasting, risk, agent, savings) allows individual modules to be upgraded or replaced independently. For example, Prophet could be swapped for an LSTM model without affecting the agent or dashboard layers.

---

# 17. Limitations

## 17.1 Data Quality Dependency
The accuracy of demand forecasts and, consequently, all downstream decisions depends on the quality and quantity of historical sales data. Products with fewer than 30 days of sales history cannot generate reliable Prophet forecasts, falling back to simpler models.

## 17.2 Black Swan Events
The system cannot predict unprecedented events such as pandemics, sudden regulatory changes, or natural disasters that have no historical precedent. While the RAG pipeline can surface past risk events for context, truly novel disruptions require human judgment.

## 17.3 Prophet Model Constraints
Prophet performs best with at least 2 years of daily data and works optimally for demand patterns that exhibit clear seasonal periodicity. Products with highly irregular, event-driven demand (e.g., promotional spikes) may see less accurate forecasts.

## 17.4 LLM Response Variability
The OpenAI GPT-4o-mini model may produce slightly different reasoning and quantity recommendations across identical runs due to the stochastic nature of language model inference. While the deterministic fallback ensures consistency when the LLM is unavailable, this variability is an inherent characteristic of LLM-based systems.

## 17.5 Single-Warehouse Model
The current implementation assumes a single warehouse/location. Multi-warehouse inventory optimization with inter-warehouse transfers is not supported in the MVP.

## 17.6 Supplier Data Assumptions
Supplier reliability scores and price ratings are initialized based on configuration rather than being dynamically updated from actual delivery performance. Real-world deployment would require supplier performance tracking and score adjustment.

## 17.7 No Real-Time POS Integration
The system operates on batch-loaded data rather than a real-time point-of-sale feed. In a production environment, sales data would need to flow continuously from POS systems to keep forecasts current.

---

# 18. Future Enhancements

## 18.1 Advanced Forecasting Models
Replace or augment Prophet with deep learning models such as LSTM (Long Short-Term Memory) networks or Transformer-based architectures (e.g., Temporal Fusion Transformers) that can capture non-linear demand relationships and incorporate multiple external features simultaneously.

## 18.2 Real-Time ERP Integration
Integrate with enterprise resource planning systems (SAP, Oracle, Microsoft Dynamics) to pull live inventory and sales data, enabling truly real-time monitoring rather than batch processing.

## 18.3 Multi-Agent Collaboration
Implement specialized agents for different product categories (grains, perishables, textiles) that collaborate through a meta-agent, allowing category-specific expertise and parallel processing.

## 18.4 Mobile Application
Develop a companion mobile app for warehouse managers to receive push notifications for critical stockout alerts, approve draft purchase orders on the go, and view key dashboard metrics from anywhere.

## 18.5 Automated Supplier Communication
Extend the PO automation pipeline to automatically send purchase orders to suppliers via email or API, track order confirmations, and update expected delivery dates in real time.

## 18.6 Multi-Warehouse Optimization
Support multiple warehouse locations with inter-warehouse transfer recommendations, enabling the system to balance inventory across locations rather than treating each warehouse independently.

## 18.7 A/B Testing for Reorder Strategies
Implement experimentation infrastructure to test different reorder strategies (e.g., aggressive vs. conservative safety stock levels) on subsets of products, measuring cost impact and selecting the optimal approach data-driven.

## 18.8 Anomaly Detection
Add automated anomaly detection on sales data to flag unusual demand spikes or drops in real time, triggering immediate agent evaluation rather than waiting for scheduled scans.

## 18.9 Sustainability Metrics
Track and optimize for sustainability: minimize waste from expired perishables, reduce transportation carbon footprint by batching orders, and prefer suppliers with better environmental ratings.

---

# 19. Conclusion

The **AI-Powered Supply Chain Optimization Agent** demonstrates how modern artificial intelligence technologies can be composed into a practical, end-to-end system that transforms inventory management from a reactive, manual process into a proactive, data-driven operation.

By combining **Prophet's robust time-series forecasting** with a **LangChain ReAct agent** backed by **OpenAI GPT-4o-mini**, the system autonomously monitors inventory levels, predicts future demand with quantified uncertainty, assesses supply chain risks through **RAG-based semantic search**, factors in live weather conditions, and generates purchase orders with transparent chain-of-thought reasoning — all without requiring human intervention.

The project successfully integrates multiple AI paradigms into a coherent pipeline:
- **Statistical forecasting** (Prophet) for demand prediction with seasonal pattern detection
- **Retrieval-Augmented Generation** (ChromaDB RAG) for contextual risk intelligence
- **Agentic reasoning** (ReAct + GPT-4o-mini) for autonomous, multi-factor decision-making
- **Multi-criteria optimization** for supplier selection balancing cost, reliability, and speed
- **Interactive visualization** (Streamlit + Plotly) for stakeholder communication and monitoring

Testing with both synthetic seasonal data and agriculture-specific datasets (15 crop products across varied stock scenarios) demonstrates the system's ability to:
- Identify stockout risks days in advance through demand-rate analysis
- Generate optimized purchase orders that balance cost, reliability, and delivery speed
- Adapt decisions based on weather conditions and risk intelligence
- Project monthly cost savings from reduced overstock waste and prevented lost sales

The **interactive Streamlit dashboard** provides stakeholders with immediate visibility into inventory health, demand trends, risk alerts, and cost optimization opportunities through nine specialized pages — from the high-level KPI overview to detailed per-product savings analysis.

For small and medium businesses, this system represents a significant capability upgrade: enterprise-grade demand planning and autonomous procurement, accessible through an intuitive web interface, without the cost and complexity of traditional ERP implementations. The projected **15–25% reduction in inventory-related costs** — from both waste elimination and stockout prevention — demonstrates meaningful business value that justifies the technology investment.

The modular architecture ensures the system can evolve: Prophet can be augmented with LSTM models as more data accumulates, the single agent can grow into a multi-agent collaboration, and the batch-processing approach can transition to real-time ERP integration. The foundation built in this project provides a solid platform for continuous improvement in supply chain intelligence.

This project affirms that the convergence of time-series forecasting, large language models, vector databases, and interactive dashboards creates a powerful toolkit for solving real-world business optimization problems — bringing AI-powered supply chain management within reach of organizations of every size.

---

*End of Report*
