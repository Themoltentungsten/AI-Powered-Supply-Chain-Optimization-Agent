# ═══════════════════════════════════════════════════════════════════════
#  DAY 1: Streamlit skeleton — page layout, sidebar navigation
#  DAY 2: Raw data display (inventory table, sales table, weather card)
#  DAY 3: Prophet forecast graphs + confidence intervals, risk RAG search
#  DAY 4: Agent Orchestration page — ReAct agent, PO generation, CoT
# ═══════════════════════════════════════════════════════════════════════

import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

API_BASE = "http://localhost:8001/api/v1"

# ── DAY 1 START: Page config and sidebar ─────────────────────────────
st.set_page_config(
    page_title="Supply Chain Optimization Agent",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Inventory", "Demand Forecasting", "Purchase Orders",
     "Risk Alerts", "Weather", "Agent Orchestration", "Data Manager", "Savings Report"],
)
# ── DAY 1 END ────────────────────────────────────────────────────────


def fetch(endpoint: str, method: str = "get", timeout: int = 30, **kwargs):
    try:
        fn = getattr(requests, method)
        resp = fn(f"{API_BASE}{endpoint}", timeout=timeout, **kwargs)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.warning("Backend API is not running. Start: `uvicorn backend.app.main:app --reload`")
        return None
    except requests.exceptions.HTTPError as e:
        st.error(f"API Error {e.response.status_code}: {e.response.text}")
        return None
    except Exception as e:
        st.error(f"Error: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════
#  DASHBOARD PAGE
# ══════════════════════════════════════════════════════════════════════

if page == "Dashboard":
    # ── DAY 1 START: Dashboard layout ────────────────────────────────
    st.title("Supply Chain Optimization Dashboard")
    st.markdown("Real-time overview of inventory, forecasting, and supply chain health.")
    # ── DAY 1 END ────────────────────────────────────────────────────

    # ── DAY 2 START: Live metric cards + inventory chart ─────────────
    inventory_data = fetch("/inventory")
    if inventory_data:
        col1, col2, col3, col4 = st.columns(4)
        total_products = len(inventory_data)
        low_stock = sum(1 for item in inventory_data if item["needs_reorder"])
        total_units = sum(item["quantity_on_hand"] for item in inventory_data)

        col1.metric("Total Products", total_products)
        col2.metric("Low Stock Alerts", low_stock, delta=f"-{low_stock}" if low_stock else "0")
        col3.metric("Total Units in Stock", f"{total_units:,}")
        col4.metric("Reorder Rate", f"{low_stock}/{total_products}")

        st.subheader("Inventory Status Overview")
        df = pd.DataFrame(inventory_data)
        if not df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df["product_name"], y=df["quantity_on_hand"],
                name="Current Stock", marker_color="#2563eb",
            ))
            fig.add_trace(go.Scatter(
                x=df["product_name"], y=df["reorder_point"],
                name="Reorder Point", mode="lines+markers",
                line=dict(color="#ef4444", dash="dash"),
            ))
            fig.add_trace(go.Scatter(
                x=df["product_name"], y=df["safety_stock"],
                name="Safety Stock", mode="lines+markers",
                line=dict(color="#f59e0b", dash="dot"),
            ))
            fig.update_layout(
                xaxis_title="Product", yaxis_title="Quantity",
                barmode="group", template="plotly_white", height=450,
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run `python database/seed_data.py` then start the backend to see data.")
    # ── DAY 2 END ────────────────────────────────────────────────────


# ══════════════════════════════════════════════════════════════════════
#  INVENTORY PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "Inventory":
    st.title("Inventory Management")

    # ── DAY 2 START: Raw inventory data table ────────────────────────
    inventory_data = fetch("/inventory")
    if inventory_data:
        df = pd.DataFrame(inventory_data)

        st.subheader("All Inventory")
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("Products Below Reorder Point")
        low = df[df["needs_reorder"] == True]
        if not low.empty:
            st.dataframe(
                low.style.apply(
                    lambda x: [
                        "background-color: #7f1d1d; color: #fecaca"
                    ] * len(x),
                    axis=1,
                ),
                use_container_width=True, hide_index=True,
            )
        else:
            st.success("All products are above reorder point.")
    else:
        st.info("Backend not connected.")
    # ── DAY 2 END ────────────────────────────────────────────────────


# ══════════════════════════════════════════════════════════════════════
#  DEMAND FORECASTING PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "Demand Forecasting":
    # ── DAY 1 START: Forecast page layout ────────────────────────────
    st.title("Demand Forecasting")
    st.markdown("Prophet-based demand predictions with confidence intervals.")
    # ── DAY 1 END ────────────────────────────────────────────────────

    products = fetch("/products")
    if products:
        product_options = {p["name"]: p["product_id"] for p in products}
        selected = st.selectbox("Select Product", list(product_options.keys()))
        product_id = product_options[selected]

        # ── DAY 2 START: Historical sales display ────────────────────
        sales = fetch(f"/sales-history/{product_id}")
        if sales:
            st.subheader("Historical Sales Data")
            sales_df = pd.DataFrame(sales)
            sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"])
            sales_df = sales_df.sort_values("sale_date")

            col_chart, col_table = st.columns([3, 1])
            with col_chart:
                fig = px.line(
                    sales_df, x="sale_date", y="quantity_sold",
                    title=f"Daily Sales — {selected}",
                    template="plotly_white",
                )
                fig.update_traces(line_color="#2563eb")
                st.plotly_chart(fig, use_container_width=True)
            with col_table:
                st.metric("Total Records", f"{len(sales_df):,}")
                st.metric("Avg Daily Sales", f"{sales_df['quantity_sold'].mean():.1f}")
                st.metric("Max Daily Sales", int(sales_df["quantity_sold"].max()))
        # ── DAY 2 END ────────────────────────────────────────────────

        # ── DAY 3 START: Prophet forecast generation & display ───────
        st.subheader("Generate Demand Forecast")
        col_periods, col_btn = st.columns([1, 1])
        with col_periods:
            periods = st.slider("Forecast horizon (days)", 7, 90, 30)
        with col_btn:
            generate = st.button("Run Forecast", type="primary")

        if generate:
            with st.spinner("Running forecast model …"):
                result = fetch(
                    f"/forecasts/generate/{product_id}?periods={periods}",
                    method="post",
                )
            if result:
                st.success(f"Forecast generated using **{result['model_used']}**")

        forecasts = fetch(f"/forecasts/{product_id}")
        if forecasts:
            st.subheader("Demand Forecast with Confidence Intervals")
            fc_df = pd.DataFrame(forecasts)
            fc_df["forecast_date"] = pd.to_datetime(fc_df["forecast_date"])

            fig = go.Figure()

            if sales:
                recent = sales_df.tail(60)
                fig.add_trace(go.Scatter(
                    x=recent["sale_date"], y=recent["quantity_sold"],
                    mode="lines", name="Actual Sales",
                    line=dict(color="#64748b"),
                ))

            fig.add_trace(go.Scatter(
                x=fc_df["forecast_date"], y=fc_df["upper_bound"],
                mode="lines", name="Upper Bound",
                line=dict(width=0), showlegend=False,
            ))
            fig.add_trace(go.Scatter(
                x=fc_df["forecast_date"], y=fc_df["lower_bound"],
                mode="lines", name="Confidence Interval",
                fill="tonexty", fillcolor="rgba(37,99,235,0.15)",
                line=dict(width=0),
            ))
            fig.add_trace(go.Scatter(
                x=fc_df["forecast_date"], y=fc_df["predicted_demand"],
                mode="lines", name="Predicted Demand",
                line=dict(color="#2563eb", width=2),
            ))

            fig.update_layout(
                template="plotly_white", height=500,
                xaxis_title="Date", yaxis_title="Quantity",
                title=f"Demand Forecast — {selected}",
            )
            st.plotly_chart(fig, use_container_width=True)
        elif sales:
            st.info("Click **Run Forecast** to generate Prophet predictions.")
        # ── DAY 3 END ────────────────────────────────────────────────

    else:
        st.info("Backend not connected.")


# ══════════════════════════════════════════════════════════════════════
#  PURCHASE ORDERS PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "Purchase Orders":
    # ── DAY 1 START: PO listing ──────────────────────────────────────
    st.title("Purchase Orders")
    st.markdown("Auto-generated and manual purchase orders.")

    po_data = fetch("/purchase-orders")
    if po_data:
        df = pd.DataFrame(po_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No purchase orders yet. The agent will generate them on Day 4.")
    # ── DAY 1 END ────────────────────────────────────────────────────


# ══════════════════════════════════════════════════════════════════════
#  RISK ALERTS PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "Risk Alerts":
    st.title("Supply Chain Risk Alerts")

    # ── DAY 3 START: Risk events table + RAG search ──────────────────
    st.subheader("All Risk Events")
    risks = fetch("/risks")
    if risks:
        rdf = pd.DataFrame(risks)

        severity_colors = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
        rdf["severity_icon"] = rdf["severity"].map(severity_colors).fillna("⚪") + " " + rdf["severity"]

        st.dataframe(
            rdf[["event_date", "severity_icon", "event_type", "description",
                 "affected_suppliers", "affected_region"]],
            use_container_width=True, hide_index=True,
        )
    else:
        st.info("No risk events. Run `python database/seed_data.py` to populate.")

    st.subheader("Semantic Risk Search (RAG)")
    st.markdown("Search risk events using natural language queries.")
    query = st.text_input("Enter risk query", placeholder="e.g. supplier delay, port congestion, weather disruption")

    if query:
        results = fetch(f"/risks/search?q={query}&n=5")
        if results:
            for i, hit in enumerate(results):
                if "message" in hit:
                    st.warning(hit["message"])
                    break
                with st.expander(
                    f"**{hit.get('event_type', 'unknown')}** — "
                    f"Severity: {hit.get('severity', '?')} | "
                    f"Relevance: {hit.get('relevance_score', '?')} | "
                    f"Date: {hit.get('date', '?')}",
                    expanded=(i == 0),
                ):
                    st.write(hit.get("document", ""))
    # ── DAY 3 END ────────────────────────────────────────────────────


# ══════════════════════════════════════════════════════════════════════
#  WEATHER PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "Weather":
    # ── DAY 2 START: Live weather from WeatherAPI ────────────────────
    st.title("External Weather Signals")
    st.markdown("Live weather data used as external regressors for demand forecasting.")

    location = st.text_input("Enter city or location", value="New York")
    if st.button("Fetch Weather", type="primary"):
        data = fetch(f"/weather?q={location}")
        if data:
            loc = data.get("location", {})
            cur = data.get("current", {})

            st.subheader(f"{loc.get('name')}, {loc.get('country')}")
            st.caption(f"Local time: {loc.get('localtime')}")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Temperature", f"{cur.get('temp_c')} °C")
            c2.metric("Humidity", f"{cur.get('humidity')}%")
            c3.metric("Precipitation", f"{cur.get('precip_mm')} mm")
            c4.metric("Wind", f"{cur.get('wind_kph')} kph")

            st.info(f"Condition: **{cur.get('condition')}**")
    # ── DAY 2 END ────────────────────────────────────────────────────


# ══════════════════════════════════════════════════════════════════════
#  AGENT ORCHESTRATION PAGE  (DAY 4)
# ══════════════════════════════════════════════════════════════════════

elif page == "Agent Orchestration":
    st.title("Agent Orchestration & PO Generation")
    st.markdown(
        "The **ReAct agent** monitors inventory levels, interprets demand forecasts, "
        "searches risk intelligence, selects the best supplier, and autonomously drafts "
        "Purchase Orders when stock drops below the Reorder Point (ROP)."
    )

    # ── Weather location for agent context ──────────────────────────────
    weather_loc = st.text_input(
        "Weather location (agent uses this for weather-aware decisions)",
        value="New York", key="agent_weather_loc",
    )

    # ── Single-product agent run ──────────────────────────────────────
    st.subheader("Run Agent for a Single Product")
    products = fetch("/products")
    if products:
        product_map = {p["name"]: p["product_id"] for p in products}
        sel_name = st.selectbox("Select Product", list(product_map.keys()), key="agent_prod")
        sel_id = product_map[sel_name]

        col_analysis, col_run = st.columns(2)

        with col_analysis:
            if st.button("Stock Analysis (ROP / EOQ)", key="btn_stock"):
                with st.spinner("Calculating ROP & EOQ…"):
                    data = fetch(f"/agent/stock-analysis/{sel_id}")
                if data:
                    c1, c2, c3 = st.columns(3)
                    c1.metric("On Hand", data.get("quantity_on_hand", "?"))
                    c2.metric("Reorder Point", data.get("reorder_point_calc", "?"))
                    c3.metric("EOQ", data.get("eoq_calc", "?"))

                    c4, c5, c6 = st.columns(3)
                    c4.metric("Avg Daily Demand", data.get("avg_daily_demand", "?"))
                    c5.metric("Lead Time (days)", data.get("lead_time_days", "?"))
                    c6.metric("Forecast 30d", data.get("forecast_demand_30d", "?"))

                    if data.get("needs_reorder"):
                        st.error("Stock is BELOW the Reorder Point — reorder recommended.")
                    else:
                        st.success("Stock is above the Reorder Point — no immediate action needed.")

        with col_run:
            if st.button("Run Full Agent (OpenAI)", type="primary", key="btn_agent_single"):
                with st.spinner("Agent is reasoning (fetching forecast + weather + risks via OpenAI GPT)…"):
                    result = fetch(
                        f"/agent/run/{sel_id}?location={weather_loc}",
                        method="post", timeout=120,
                    )
                if result:
                    decision = result.get("decision", "?")
                    if decision == "REORDER":
                        st.error(f"Decision: **REORDER** — Quantity: {result.get('reorder_qty', '?')}")
                    else:
                        st.success(f"Decision: **{decision}** — No reorder needed right now.")

                    if result.get("weather") and "note" not in result.get("weather", {}):
                        w = result["weather"]
                        st.subheader("Weather Context Used")
                        wc1, wc2, wc3, wc4 = st.columns(4)
                        wc1.metric("Location", w.get("name", weather_loc))
                        wc2.metric("Temp", f"{w.get('temp_c', '?')}°C")
                        wc3.metric("Humidity", f"{w.get('humidity', '?')}%")
                        wc4.metric("Condition", w.get("condition", "?"))

                    if result.get("forecast") and "warning" not in result.get("forecast", {}):
                        fc = result["forecast"]
                        st.subheader("Forecast Used")
                        fc1, fc2, fc3 = st.columns(3)
                        fc1.metric("Model", fc.get("model", "?"))
                        fc2.metric(f"Total {fc.get('forecast_days', '?')}d Demand", fc.get("total_predicted", "?"))
                        fc3.metric("Avg Daily", fc.get("avg_daily_predicted", "?"))

                    st.subheader("Chain-of-Thought Reasoning")
                    st.markdown(result.get("reasoning", "_No reasoning returned._"))

                    if result.get("purchase_order"):
                        po = result["purchase_order"]
                        st.subheader("Drafted Purchase Order")
                        po_c1, po_c2, po_c3, po_c4 = st.columns(4)
                        po_c1.metric("PO #", po.get("po_id"))
                        po_c2.metric("Supplier", po.get("supplier"))
                        po_c3.metric("Quantity", po.get("quantity"))
                        po_c4.metric("Total $", f"${po.get('total', 0):,.2f}")
                        st.info(f"Expected delivery: {po.get('expected_delivery', '?')}")

                    if result.get("supplier") and "error" not in result["supplier"]:
                        sup = result["supplier"]
                        st.subheader("Supplier Selection Details")
                        sup_c1, sup_c2, sup_c3, sup_c4 = st.columns(4)
                        sup_c1.metric("Supplier", sup.get("supplier_name"))
                        sup_c2.metric("Unit Price", f"${sup.get('unit_price', 0):.2f}")
                        sup_c3.metric("Reliability", f"{sup.get('reliability', 0):.0%}")
                        sup_c4.metric("Composite Score", f"{sup.get('composite_score', 0):.3f}")

                    if result.get("tool_log"):
                        with st.expander("Tool Call Log (debug)"):
                            for entry in result["tool_log"]:
                                st.markdown(f"**{entry['tool']}** | Input: `{entry['input']}` | Output: `{entry['output'][:200]}…`")
    else:
        st.warning("No products found. Load data via Data Manager first.")

    st.divider()

    # ── Scan all below-ROP products ───────────────────────────────────
    st.subheader("Scan All Low-Stock Products")
    st.caption(
        "The agent scans every product whose stock is at or below its Reorder Point, "
        "reasons about each, and drafts Purchase Orders as needed."
    )
    if st.button("Run Full Scan", type="primary", key="btn_scan"):
        with st.spinner("Scanning all products below ROP (this may take a minute)…"):
            scan = fetch(f"/agent/scan?location={weather_loc}", method="post", timeout=300)
        if scan:
            sc1, sc2, sc3, sc4 = st.columns(4)
            sc1.metric("Total Scanned", scan.get("total_scanned", 0))
            sc2.metric("Reorders Created", scan.get("reorders", 0))
            sc3.metric("No Reorder", scan.get("no_reorders", 0))
            sc4.metric("Errors", scan.get("errors", 0))

            for res in scan.get("results", []):
                with st.expander(
                    f"{'🔴' if res.get('decision') == 'REORDER' else '🟢'} "
                    f"{res.get('product_name', 'Unknown')} — {res.get('decision', '?')}"
                ):
                    st.markdown(res.get("reasoning", "_No reasoning._"))
                    if res.get("purchase_order"):
                        po = res["purchase_order"]
                        st.info(
                            f"PO #{po['po_id']} | Supplier: {po['supplier']} | "
                            f"Qty: {po['quantity']} | Total: ${po['total']:,.2f} | "
                            f"Delivery: {po['expected_delivery']}"
                        )

    st.divider()

    # ── Agent PO history ──────────────────────────────────────────────
    st.subheader("Agent-Generated Purchase Orders")
    po_history = fetch("/agent/po-history?limit=20")
    if po_history:
        po_df = pd.DataFrame(po_history)
        st.dataframe(po_df, use_container_width=True, hide_index=True)

        for po in po_history:
            if po.get("agent_reasoning"):
                with st.expander(f"PO #{po['po_id']} — Reasoning"):
                    st.markdown(po["agent_reasoning"])
    else:
        st.info("No agent-generated POs yet. Run the agent above to create some.")


# ══════════════════════════════════════════════════════════════════════
#  DATA MANAGER PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "Data Manager":
    st.title("Data Manager")
    st.markdown(
        "Load **Synthetic seed data** or upload a **Kaggle CSV** dataset. "
        "Switch between loaded sources, view stats, or delete them."
    )

    # ── Active source + live counts ───────────────────────────────────
    active_info = fetch("/data-sources/active")
    if active_info:
        counts = active_info.get("counts", {})
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Products", counts.get("products", 0))
        c2.metric("Sales Rows", counts.get("sales", 0))
        c3.metric("Suppliers", counts.get("suppliers", 0))
        c4.metric("Risk Events", counts.get("risk_events", 0))

        active = active_info.get("active")
        if active:
            st.success(
                f"Active source: **{active['name']}** "
                f"({active['source_type']}) — loaded {active['loaded_at'][:19] if active.get('loaded_at') else '?'}"
            )
        else:
            st.warning("No active data source. Load one below.")

    st.divider()

    # ── Load Synthetic Seed ───────────────────────────────────────────
    st.subheader("Option 1 — Load Synthetic Seed Data")
    st.caption(
        "Creates products with seasonal sales history, risk events, and suppliers. "
        "Great for Prophet forecasting demos."
    )
    if st.button("Load Synthetic Seed", type="primary", key="btn_seed"):
        with st.spinner("Clearing old data and seeding…"):
            res = fetch("/data-sources/load-seed", method="post")
        if res:
            st.success(
                f"Loaded! Products: {res['counts']['products']}, "
                f"Sales rows: {res['counts']['sales']}"
            )
            st.rerun()

    st.divider()

    # ── Load Farming Crops Dataset ────────────────────────────────────
    st.subheader("Option 2 — Load Farming / Crops Dataset")
    st.caption(
        "15 crops (rice, wheat, corn, tomatoes, mangoes, cotton, coffee, etc.) with "
        "**mixed stock levels**: some above ROP, some below ROP, some CRITICAL (below safety stock). "
        "Includes 10 agriculture-specific risk alerts (drought, pest outbreak, flooding, heatwave, etc.)."
    )
    if st.button("Load Farming Dataset", type="primary", key="btn_farming"):
        with st.spinner("Clearing old data and seeding farming crops…"):
            res = fetch("/data-sources/load-farming", method="post", timeout=120)
        if res:
            st.success(
                f"Loaded! Products: {res['counts']['products']}, "
                f"Sales rows: {res['counts']['sales']}, "
                f"Risk events: {res['counts']['risk_events']}"
            )
            st.rerun()

    st.divider()

    # ── Upload Kaggle CSV ─────────────────────────────────────────────
    st.subheader("Option 3 — Upload Kaggle CSV Dataset")
    st.caption(
        "Upload a CSV file from Kaggle (Superstore Sales, Online Retail, etc.). "
        "The system auto-detects the column format."
    )
    uploaded = st.file_uploader(
        "Choose a .csv file",
        type=["csv"],
        key="csv_upload",
    )
    max_prod = st.number_input(
        "Max products to import (0 = all)",
        min_value=0, value=0, step=10, key="max_prod_input",
    )

    if uploaded is not None:
        if st.button("Import CSV", type="primary", key="btn_csv"):
            with st.spinner(f"Importing {uploaded.name}…"):
                files = {"file": (uploaded.name, uploaded.getvalue(), "text/csv")}
                try:
                    resp = requests.post(
                        f"{API_BASE}/data-sources/load-csv",
                        files=files,
                        params={"max_products": max_prod},
                        timeout=120,
                    )
                    resp.raise_for_status()
                    res = resp.json()
                    st.success(
                        f"Imported **{uploaded.name}**! Products: {res['counts']['products']}, "
                        f"Sales rows: {res['counts']['sales']}"
                    )
                    st.rerun()
                except requests.exceptions.HTTPError as e:
                    st.error(f"Import failed: {e.response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.divider()

    # ── Load Kaggle via presets (kagglehub) ───────────────────────────
    st.subheader("Option 4 — Load Kaggle Preset (kagglehub)")
    st.caption(
        "Downloads a known retail dataset using kagglehub, then imports into PostgreSQL/DB."
    )
    kaggle_preset = st.selectbox(
        "Preset",
        ["superstore", "online-retail"],
        index=0,
        key="kaggle_preset_select",
    )
    max_prod_kaggle = st.number_input(
        "Max products to import (0 = all)",
        min_value=0,
        value=0,
        step=10,
        key="max_prod_kaggle_input",
    )
    if st.button("Load Kaggle Data", type="primary", key="btn_load_kaggle"):
        with st.spinner("Downloading + importing Kaggle dataset…"):
            resp = fetch(
                "/data-sources/load-kaggle",
                method="post",
                timeout=600,
                params={
                    "preset": kaggle_preset,
                    "max_products": int(max_prod_kaggle),
                    "dataset": None,
                },
            )
        if resp:
            st.success(
                f"Imported Kaggle data! Products: {resp['counts']['products']}, "
                f"Sales rows: {resp['counts']['sales']}"
            )
            st.rerun()

    st.divider()

    # ── All data sources list ─────────────────────────────────────────
    st.subheader("All Loaded Data Sources")
    sources = fetch("/data-sources")
    if sources:
        for src in sources:
            col_info, col_act, col_del = st.columns([5, 1, 1])
            badge = "🟢" if src["is_active"] else "⚪"
            col_info.markdown(
                f"{badge} **{src['name']}** &nbsp;|&nbsp; Type: `{src['source_type']}` "
                f"&nbsp;|&nbsp; Products: {src['product_count']} "
                f"&nbsp;|&nbsp; Sales: {src['sales_count']} "
                f"&nbsp;|&nbsp; Loaded: {src['loaded_at'][:19] if src.get('loaded_at') else '?'}"
            )
            if not src["is_active"]:
                if col_act.button("Activate", key=f"act_{src['id']}"):
                    fetch(f"/data-sources/{src['id']}/activate", method="post")
                    st.rerun()
            else:
                col_act.markdown("**Active**")
            if col_del.button("Delete", key=f"del_{src['id']}"):
                fetch(f"/data-sources/{src['id']}", method="delete")
                st.rerun()
    else:
        st.info("No data sources loaded yet.")

    st.divider()
    if st.button("Delete ALL Data Sources & Wipe Database", type="secondary"):
        fetch("/data-sources", method="delete")
        st.rerun()


# ══════════════════════════════════════════════════════════════════════
#  SAVINGS REPORT PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "Savings Report":
    # ── DAY 1 START: Placeholder ─────────────────────────────────────
    st.title("Monthly Savings Report")
    st.markdown("Projected cost savings from demand forecasting and automated reordering.")
    st.info("Savings report will be populated after the full pipeline runs (Day 5).")
    # ── DAY 1 END ────────────────────────────────────────────────────


# ── DAY 1 START: Sidebar footer ──────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.caption("AI-Powered Supply Chain Optimization Agent v0.1.0")
# ── DAY 1 END ────────────────────────────────────────────────────────
