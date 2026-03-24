-- ============================================================================
-- AI-Powered Supply Chain Optimization Agent
-- PostgreSQL Database Schema
-- ============================================================================

-- Products: Master catalog of all products tracked by the system
CREATE TABLE IF NOT EXISTS products (
    product_id      SERIAL PRIMARY KEY,
    sku             VARCHAR(50) UNIQUE NOT NULL,
    name            VARCHAR(200) NOT NULL,
    category        VARCHAR(100),
    unit_cost       NUMERIC(12, 2) NOT NULL,
    selling_price   NUMERIC(12, 2) NOT NULL,
    unit_of_measure VARCHAR(20) DEFAULT 'units',
    lead_time_days  INTEGER DEFAULT 7,
    is_active       BOOLEAN DEFAULT TRUE,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Suppliers: Directory of all suppliers with reliability tracking
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id       SERIAL PRIMARY KEY,
    name              VARCHAR(200) NOT NULL,
    contact_email     VARCHAR(200),
    phone             VARCHAR(50),
    address           TEXT,
    avg_lead_time_days INTEGER NOT NULL DEFAULT 7,
    reliability_score  NUMERIC(3, 2) DEFAULT 0.90,  -- 0.00 to 1.00
    price_rating       NUMERIC(3, 2) DEFAULT 0.50,  -- lower is cheaper
    is_active          BOOLEAN DEFAULT TRUE,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product-Supplier mapping (many-to-many with supplier-specific pricing)
CREATE TABLE IF NOT EXISTS product_suppliers (
    product_id   INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
    supplier_id  INTEGER REFERENCES suppliers(supplier_id) ON DELETE CASCADE,
    unit_price   NUMERIC(12, 2) NOT NULL,
    min_order_qty INTEGER DEFAULT 1,
    lead_time_days INTEGER,
    PRIMARY KEY (product_id, supplier_id)
);

-- Inventory: Current stock levels and reorder parameters
CREATE TABLE IF NOT EXISTS inventory (
    inventory_id    SERIAL PRIMARY KEY,
    product_id      INTEGER UNIQUE REFERENCES products(product_id) ON DELETE CASCADE,
    quantity_on_hand INTEGER NOT NULL DEFAULT 0,
    reorder_point    INTEGER NOT NULL DEFAULT 50,
    reorder_qty      INTEGER NOT NULL DEFAULT 100,  -- EOQ
    safety_stock     INTEGER NOT NULL DEFAULT 20,
    warehouse_location VARCHAR(50),
    last_restock_date  DATE,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales History: Daily POS records for demand forecasting
CREATE TABLE IF NOT EXISTS sales_history (
    sale_id      SERIAL PRIMARY KEY,
    product_id   INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
    sale_date    DATE NOT NULL,
    quantity_sold INTEGER NOT NULL,
    revenue      NUMERIC(12, 2),
    channel      VARCHAR(50) DEFAULT 'in-store',  -- in-store, online, wholesale
    promotion_active BOOLEAN DEFAULT FALSE,
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purchase Orders: Auto-generated or manual POs
CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id           SERIAL PRIMARY KEY,
    supplier_id     INTEGER REFERENCES suppliers(supplier_id),
    status          VARCHAR(30) DEFAULT 'draft',  -- draft, pending_approval, approved, shipped, received, cancelled
    total_amount    NUMERIC(14, 2),
    order_date      DATE DEFAULT CURRENT_DATE,
    expected_delivery DATE,
    actual_delivery  DATE,
    generated_by    VARCHAR(50) DEFAULT 'agent',  -- agent or manual
    agent_reasoning TEXT,  -- chain-of-thought from the LLM agent
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Purchase Order Line Items
CREATE TABLE IF NOT EXISTS purchase_order_items (
    po_item_id   SERIAL PRIMARY KEY,
    po_id        INTEGER REFERENCES purchase_orders(po_id) ON DELETE CASCADE,
    product_id   INTEGER REFERENCES products(product_id),
    quantity     INTEGER NOT NULL,
    unit_price   NUMERIC(12, 2) NOT NULL,
    line_total   NUMERIC(14, 2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);

-- Risk Events: Supply chain disruption logs for RAG pipeline
CREATE TABLE IF NOT EXISTS risk_events (
    event_id     SERIAL PRIMARY KEY,
    event_type   VARCHAR(100) NOT NULL,  -- port_congestion, weather_disruption, supplier_bankruptcy, etc.
    severity     VARCHAR(20) DEFAULT 'medium',  -- low, medium, high, critical
    description  TEXT NOT NULL,
    affected_suppliers TEXT,  -- comma-separated supplier IDs or names
    affected_region VARCHAR(100),
    event_date   DATE NOT NULL,
    resolved     BOOLEAN DEFAULT FALSE,
    resolution_notes TEXT,
    source       VARCHAR(200),  -- news_api, weather_api, manual
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weather Data: Cached external weather signals used as forecast regressors
CREATE TABLE IF NOT EXISTS weather_data (
    weather_id    SERIAL PRIMARY KEY,
    location      VARCHAR(100) NOT NULL,
    record_date   DATE NOT NULL,
    temp_avg      NUMERIC(5, 2),
    temp_min      NUMERIC(5, 2),
    temp_max      NUMERIC(5, 2),
    humidity      NUMERIC(5, 2),
    precipitation NUMERIC(7, 2),
    weather_desc  VARCHAR(100),
    fetched_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(location, record_date)
);

-- Demand Forecasts: Stored forecast results from Prophet
CREATE TABLE IF NOT EXISTS demand_forecasts (
    forecast_id   SERIAL PRIMARY KEY,
    product_id    INTEGER REFERENCES products(product_id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    predicted_demand NUMERIC(10, 2) NOT NULL,
    lower_bound   NUMERIC(10, 2),
    upper_bound   NUMERIC(10, 2),
    model_version VARCHAR(50) DEFAULT 'prophet_v1',
    generated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, forecast_date, model_version)
);

-- Indexes for query performance
CREATE INDEX idx_sales_product_date ON sales_history(product_id, sale_date);
CREATE INDEX idx_sales_date ON sales_history(sale_date);
CREATE INDEX idx_inventory_product ON inventory(product_id);
CREATE INDEX idx_po_status ON purchase_orders(status);
CREATE INDEX idx_po_supplier ON purchase_orders(supplier_id);
CREATE INDEX idx_forecast_product_date ON demand_forecasts(product_id, forecast_date);
CREATE INDEX idx_weather_location_date ON weather_data(location, record_date);
CREATE INDEX idx_risk_events_date ON risk_events(event_date);
CREATE INDEX idx_risk_events_severity ON risk_events(severity);
