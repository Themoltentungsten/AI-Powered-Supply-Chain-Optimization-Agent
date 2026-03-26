# ═══════════════════════════════════════════════════════════════════════
#  DAY 1: Streamlit skeleton — page layout, sidebar navigation
#  DAY 2: Raw data display (inventory table, sales table, weather card)
#  DAY 3: Prophet forecast graphs + confidence intervals, risk RAG search
#  DAY 4: Agent Orchestration page — ReAct agent, PO generation, CoT
#  DAY 5: Dashboard polish, stockout predictions, savings report, demo UI
# ═══════════════════════════════════════════════════════════════════════

import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

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
#  DASHBOARD PAGE  (DAY 5: enhanced with stockout predictions + risk)
# ══════════════════════════════════════════════════════════════════════

if page == "Dashboard":
    st.title("Supply Chain Optimization Dashboard")
    st.markdown("Real-time overview of inventory health, predicted stockouts, and supply chain risk status.")

    inventory_data = fetch("/inventory")
    savings_data = fetch("/savings/report")

    if inventory_data:
        total_products = len(inventory_data)
        low_stock = sum(1 for item in inventory_data if item["needs_reorder"])
        total_units = sum(item["quantity_on_hand"] for item in inventory_data)

        # ── DAY 5: Enhanced KPI row ──────────────────────────────────
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Products", total_products)
        c2.metric("Low Stock Alerts", low_stock, delta=f"-{low_stock}" if low_stock else "0")
        c3.metric("Total Units", f"{total_units:,}")
        c4.metric("Reorder Rate", f"{round(low_stock/max(total_products,1)*100)}%")

        if savings_data:
            s = savings_data["summary"]
            c5.metric("Critical Stockouts", s["critical_count"], delta=f"-{s['critical_count']}" if s["critical_count"] else "0")

        # ── Inventory bar chart with ROP + safety lines ───────────────
        st.subheader("Inventory Levels vs Reorder Points")
        df = pd.DataFrame(inventory_data)
        if not df.empty:
            fig = go.Figure()
            colors = ["#ef4444" if r else "#2563eb" for r in df["needs_reorder"]]
            fig.add_trace(go.Bar(
                x=df["product_name"], y=df["quantity_on_hand"],
                name="Current Stock", marker_color=colors,
            ))
            fig.add_trace(go.Scatter(
                x=df["product_name"], y=df["reorder_point"],
                name="Reorder Point (ROP)", mode="lines+markers",
                line=dict(color="#ef4444", dash="dash", width=2),
            ))
            fig.add_trace(go.Scatter(
                x=df["product_name"], y=df["safety_stock"],
                name="Safety Stock", mode="lines+markers",
                line=dict(color="#f59e0b", dash="dot", width=2),
            ))
            fig.update_layout(
                xaxis_title="Product", yaxis_title="Quantity",
                barmode="group", template="plotly_white", height=450,
                legend=dict(orientation="h", yanchor="bottom", y=1.02),
            )
            st.plotly_chart(fig, use_container_width=True)

        # ── DAY 5: Stockout prediction timeline ──────────────────────
        if savings_data and savings_data.get("products"):
            st.subheader("Predicted Stockout Dates")
            st.caption("When each product will run out of stock based on current demand rate.")

            sp = pd.DataFrame(savings_data["products"])
            sp["stockout_date"] = pd.to_datetime(sp["stockout_date"])
            sp = sp.sort_values("days_of_stock")

            risk_colors = {"critical": "#ef4444", "warning": "#f59e0b", "ok": "#22c55e"}
            sp["color"] = sp["stockout_risk"].map(risk_colors)

            fig2 = go.Figure()
            fig2.add_trace(go.Bar(
                x=sp["product_name"], y=sp["days_of_stock"],
                marker_color=sp["color"].tolist(),
                text=sp["days_of_stock"].apply(lambda d: f"{d:.0f}d"),
                textposition="outside",
                hovertext=sp.apply(lambda r: f"Stockout: {r['stockout_date'].strftime('%Y-%m-%d')}<br>Demand: {r['avg_daily_demand']}/day", axis=1),
            ))
            fig2.add_hline(y=7, line_dash="dash", line_color="#ef4444", annotation_text="Critical (7 days)")
            fig2.add_hline(y=14, line_dash="dot", line_color="#f59e0b", annotation_text="Warning (14 days)")
            fig2.update_layout(
                yaxis_title="Days of Stock Remaining",
                template="plotly_white", height=400, showlegend=False,
            )
            st.plotly_chart(fig2, use_container_width=True)

        # ── DAY 5: Risk summary cards ─────────────────────────────────
        risks = fetch("/risks")
        if risks:
            st.subheader("Active Risk Alerts")
            for r in risks[:5]:
                severity_map = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                icon = severity_map.get(r.get("severity", ""), "⚪")
                st.markdown(
                    f"{icon} **{r['event_type'].replace('_',' ').title()}** — "
                    f"{r['description'][:120]}… "
                    f"*(Affected: {r.get('affected_suppliers', 'N/A')})*"
                )
    else:
        st.info("Load data via **Data Manager** then refresh this page.")


# ══════════════════════════════════════════════════════════════════════
#  INVENTORY PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "Inventory":
    st.title("Inventory Management")

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
                    lambda x: ["background-color: #7f1d1d; color: #fecaca"] * len(x), axis=1,
                ),
                use_container_width=True, hide_index=True,
            )
        else:
            st.success("All products are above reorder point.")
    else:
        st.info("Backend not connected.")


# ══════════════════════════════════════════════════════════════════════
#  DEMAND FORECASTING PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "Demand Forecasting":
    st.title("Demand Forecasting")
    st.markdown("Prophet-based demand predictions with confidence intervals.")

    products = fetch("/products")
    if products:
        product_options = {p["name"]: p["product_id"] for p in products}
        selected = st.selectbox("Select Product", list(product_options.keys()))
        product_id = product_options[selected]

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
                    title=f"Daily Sales — {selected}", template="plotly_white",
                )
                fig.update_traces(line_color="#2563eb")
                st.plotly_chart(fig, use_container_width=True)
            with col_table:
                st.metric("Total Records", f"{len(sales_df):,}")
                st.metric("Avg Daily Sales", f"{sales_df['quantity_sold'].mean():.1f}")
                st.metric("Max Daily Sales", int(sales_df["quantity_sold"].max()))

        st.subheader("Generate Demand Forecast")
        col_periods, col_btn = st.columns([1, 1])
        with col_periods:
            periods = st.slider("Forecast horizon (days)", 7, 90, 30)
        with col_btn:
            generate = st.button("Run Forecast", type="primary")

        if generate:
            with st.spinner("Running forecast model …"):
                result = fetch(f"/forecasts/generate/{product_id}?periods={periods}", method="post")
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
                    mode="lines", name="Actual Sales", line=dict(color="#64748b"),
                ))
            fig.add_trace(go.Scatter(
                x=fc_df["forecast_date"], y=fc_df["upper_bound"],
                mode="lines", name="Upper Bound", line=dict(width=0), showlegend=False,
            ))
            fig.add_trace(go.Scatter(
                x=fc_df["forecast_date"], y=fc_df["lower_bound"],
                mode="lines", name="Confidence Interval",
                fill="tonexty", fillcolor="rgba(37,99,235,0.15)", line=dict(width=0),
            ))
            fig.add_trace(go.Scatter(
                x=fc_df["forecast_date"], y=fc_df["predicted_demand"],
                mode="lines", name="Predicted Demand", line=dict(color="#2563eb", width=2),
            ))
            fig.update_layout(
                template="plotly_white", height=500,
                xaxis_title="Date", yaxis_title="Quantity",
                title=f"Demand Forecast — {selected}",
            )
            st.plotly_chart(fig, use_container_width=True)
        elif sales:
            st.info("Click **Run Forecast** to generate Prophet predictions.")
    else:
        st.info("Backend not connected.")


# ══════════════════════════════════════════════════════════════════════
#  PURCHASE ORDERS PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "Purchase Orders":
    st.title("Purchase Orders")
    st.markdown("Auto-generated and manual purchase orders.")

    po_data = fetch("/purchase-orders")
    if po_data:
        df = pd.DataFrame(po_data)
        agent_count = len(df[df["generated_by"] == "agent"])
        c1, c2, c3 = st.columns(3)
        c1.metric("Total POs", len(df))
        c2.metric("Agent-Generated", agent_count)
        c3.metric("Total Value", f"${df['total_amount'].sum():,.2f}" if "total_amount" in df.columns else "$0")
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No purchase orders yet. Use **Agent Orchestration** to generate them.")


# ══════════════════════════════════════════════════════════════════════
#  RISK ALERTS PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "Risk Alerts":
    st.title("Supply Chain Risk Alerts")

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

        sev_counts = rdf["severity"].value_counts()
        fig = px.pie(values=sev_counts.values, names=sev_counts.index,
                     title="Risk Severity Distribution",
                     color_discrete_map={"critical": "#ef4444", "high": "#f97316", "medium": "#eab308", "low": "#22c55e"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No risk events. Load data via **Data Manager**.")

    st.subheader("Semantic Risk Search (RAG)")
    st.markdown("Search risk events using natural language queries.")
    query = st.text_input("Enter risk query", placeholder="e.g. drought, pest outbreak, flood, supplier delay")
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


# ══════════════════════════════════════════════════════════════════════
#  WEATHER PAGE
# ══════════════════════════════════════════════════════════════════════

elif page == "Weather":
    st.title("External Weather Signals")
    st.markdown("Live weather data used as external signals for supply chain decisions.")

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


# ══════════════════════════════════════════════════════════════════════
#  AGENT ORCHESTRATION PAGE  (DAY 4)
# ══════════════════════════════════════════════════════════════════════

elif page == "Agent Orchestration":
    st.title("Agent Orchestration & PO Generation")
    st.markdown(
        "The **ReAct agent** monitors inventory levels, interprets demand forecasts, "
        "fetches live weather, searches risk intelligence, selects the best supplier, "
        "and autonomously drafts Purchase Orders when stock drops below the Reorder Point."
    )

    weather_loc = st.text_input(
        "Weather location (agent uses this for weather-aware decisions)",
        value="New York", key="agent_weather_loc",
    )

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
                        st.success("Stock is above the Reorder Point.")

        with col_run:
            if st.button("Run Full Agent (OpenAI)", type="primary", key="btn_agent_single"):
                with st.spinner("Agent is reasoning (forecast + weather + risks via OpenAI GPT)…"):
                    result = fetch(f"/agent/run/{sel_id}?location={weather_loc}", method="post", timeout=120)
                if result:
                    decision = result.get("decision", "?")
                    if decision == "REORDER":
                        st.error(f"Decision: **REORDER** — Quantity: {result.get('reorder_qty', '?')}")
                    else:
                        st.success(f"Decision: **{decision}** — No reorder needed.")

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

    st.subheader("Scan All Low-Stock Products")
    st.caption("The agent scans every product below its Reorder Point and drafts POs as needed.")
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
        "Load **Synthetic seed data**, **Farming crops**, or upload a **Kaggle CSV** dataset. "
        "Switch between loaded sources, view stats, or delete them."
    )

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

    st.subheader("Option 1 — Load Synthetic Seed Data")
    st.caption("Creates products with seasonal sales history, risk events, and suppliers.")
    if st.button("Load Synthetic Seed", type="primary", key="btn_seed"):
        with st.spinner("Clearing old data and seeding…"):
            res = fetch("/data-sources/load-seed", method="post")
        if res:
            st.success(f"Loaded! Products: {res['counts']['products']}, Sales: {res['counts']['sales']}")
            st.rerun()

    st.divider()

    st.subheader("Option 2 — Load Farming / Crops Dataset")
    st.caption(
        "15 crops with **mixed stock levels** (above ROP, below ROP, critical) and "
        "10 agriculture-specific risk alerts (drought, pests, floods, heatwave)."
    )
    if st.button("Load Farming Dataset", type="primary", key="btn_farming"):
        with st.spinner("Clearing old data and seeding farming crops…"):
            res = fetch("/data-sources/load-farming", method="post", timeout=120)
        if res:
            st.success(f"Loaded! Products: {res['counts']['products']}, Sales: {res['counts']['sales']}, Risks: {res['counts']['risk_events']}")
            st.rerun()

    st.divider()

    st.subheader("Option 3 — Upload Kaggle CSV Dataset")
    st.caption("Upload a CSV file from Kaggle. The system auto-detects the column format.")
    uploaded = st.file_uploader("Choose a .csv file", type=["csv"], key="csv_upload")
    max_prod = st.number_input("Max products to import (0 = all)", min_value=0, value=0, step=10, key="max_prod_input")
    if uploaded is not None:
        if st.button("Import CSV", type="primary", key="btn_csv"):
            with st.spinner(f"Importing {uploaded.name}…"):
                files = {"file": (uploaded.name, uploaded.getvalue(), "text/csv")}
                try:
                    resp = requests.post(f"{API_BASE}/data-sources/load-csv", files=files, params={"max_products": max_prod}, timeout=120)
                    resp.raise_for_status()
                    res = resp.json()
                    st.success(f"Imported **{uploaded.name}**! Products: {res['counts']['products']}, Sales: {res['counts']['sales']}")
                    st.rerun()
                except requests.exceptions.HTTPError as e:
                    st.error(f"Import failed: {e.response.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.divider()

    st.subheader("Option 4 — Load Kaggle Preset (kagglehub)")
    st.caption("Downloads a known retail dataset using kagglehub, then imports into DB.")
    kaggle_preset = st.selectbox("Preset", ["superstore", "online-retail"], key="kaggle_preset_select")
    max_prod_kaggle = st.number_input("Max products (0=all)", min_value=0, value=0, step=10, key="max_prod_kaggle_input")
    if st.button("Load Kaggle Data", type="primary", key="btn_load_kaggle"):
        with st.spinner("Downloading + importing Kaggle dataset…"):
            resp = fetch("/data-sources/load-kaggle", method="post", timeout=600, params={"preset": kaggle_preset, "max_products": int(max_prod_kaggle), "dataset": None})
        if resp:
            st.success(f"Imported Kaggle data! Products: {resp['counts']['products']}, Sales: {resp['counts']['sales']}")
            st.rerun()

    st.divider()
    st.subheader("All Loaded Data Sources")
    sources = fetch("/data-sources")
    if sources:
        for src in sources:
            col_info, col_act, col_del = st.columns([5, 1, 1])
            badge = "🟢" if src["is_active"] else "⚪"
            col_info.markdown(
                f"{badge} **{src['name']}** | Type: `{src['source_type']}` "
                f"| Products: {src['product_count']} | Sales: {src['sales_count']} "
                f"| Loaded: {src['loaded_at'][:19] if src.get('loaded_at') else '?'}"
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
#  SAVINGS REPORT PAGE  (DAY 5: full implementation)
# ══════════════════════════════════════════════════════════════════════

elif page == "Savings Report":
    st.title("Monthly Savings Report")
    st.markdown(
        "Projected cost savings from demand forecasting and automated reordering. "
        "Shows overstock holding costs, stockout lost-sales estimates, and total optimization potential."
    )

    data = fetch("/savings/report")
    if data and data.get("summary"):
        s = data["summary"]

        # ── KPI cards ─────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Potential Savings", f"${s['total_potential_savings']:,.2f}")
        c2.metric("Overstock Holding Cost", f"${s['total_overstock_cost']:,.2f}")
        c3.metric("Stockout Lost Sales", f"${s['total_stockout_cost']:,.2f}")
        c4.metric("Agent POs Created", s["agent_orders_count"])

        c5, c6, c7, c8 = st.columns(4)
        c5.metric("Agent PO Value", f"${s['agent_orders_value']:,.2f}")
        c6.metric("Critical Products", s["critical_count"])
        c7.metric("Warning Products", s["warning_count"])
        c8.metric("Healthy Products", s["ok_count"])

        # ── Savings breakdown pie chart ───────────────────────────────
        st.subheader("Cost Breakdown")
        col_pie, col_bar = st.columns(2)
        with col_pie:
            fig_pie = go.Figure(data=[go.Pie(
                labels=["Overstock Holding Cost", "Stockout Lost Sales"],
                values=[s["total_overstock_cost"], s["total_stockout_cost"]],
                marker_colors=["#f59e0b", "#ef4444"],
                hole=0.4,
            )])
            fig_pie.update_layout(title="Waste vs Lost Sales", height=350)
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_bar:
            prods = pd.DataFrame(data["products"])
            if not prods.empty:
                prods = prods.sort_values("potential_savings", ascending=False).head(10)
                fig_bar = px.bar(
                    prods, x="product_name", y="potential_savings",
                    color="stockout_risk",
                    color_discrete_map={"critical": "#ef4444", "warning": "#f59e0b", "ok": "#22c55e"},
                    title="Top 10 Products by Savings Potential",
                    template="plotly_white",
                )
                fig_bar.update_layout(height=350, xaxis_title="", yaxis_title="Savings ($)")
                st.plotly_chart(fig_bar, use_container_width=True)

        # ── Detailed product table ────────────────────────────────────
        st.subheader("Per-Product Analysis")
        prods_all = pd.DataFrame(data["products"])
        if not prods_all.empty:
            display_cols = ["product_name", "quantity_on_hand", "reorder_point", "avg_daily_demand",
                           "days_of_stock", "stockout_date", "stockout_risk", "overstock_cost",
                           "stockout_cost", "potential_savings"]
            st.dataframe(
                prods_all[display_cols].sort_values("days_of_stock"),
                use_container_width=True, hide_index=True,
            )

        # ── Business impact narrative ─────────────────────────────────
        st.subheader("Business Impact Summary")
        st.markdown(f"""
**The AI-Powered Supply Chain Agent can save an estimated ${s['total_potential_savings']:,.2f}/month** by:

- **Reducing overstock waste:** ${s['total_overstock_cost']:,.2f}/month in excess holding costs can be eliminated through precise demand-driven reordering.
- **Preventing lost sales:** ${s['total_stockout_cost']:,.2f}/month in estimated revenue loss from stockouts can be avoided by proactive restocking.
- **{s['critical_count']} products** are at critical risk of stockout within 7 days.
- **{s['warning_count']} products** will run out within 14 days without intervention.
- The agent has already created **{s['agent_orders_count']} purchase orders** worth **${s['agent_orders_value']:,.2f}** to address these gaps.

*These projections are based on 90-day historical demand, current inventory levels, and standard holding cost assumptions (20% annual carrying cost).*
        """)
    else:
        st.info("Load data via **Data Manager** first, then return here to see savings analysis.")


# ── Sidebar footer ────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.caption("AI-Powered Supply Chain Optimization Agent v0.2.0")
