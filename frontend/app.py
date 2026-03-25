# ═══════════════════════════════════════════════════════════════════════
#  DAY 1: Streamlit skeleton — page layout, sidebar navigation
#  DAY 2: Raw data display (inventory table, sales table, weather card)
#  DAY 3: Prophet forecast graphs + confidence intervals, risk RAG search
# ═══════════════════════════════════════════════════════════════════════

import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

API_BASE = "http://localhost:8000/api/v1"

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
     "Risk Alerts", "Weather", "Savings Report"],
)
# ── DAY 1 END ────────────────────────────────────────────────────────


def fetch(endpoint: str, method: str = "get", **kwargs):
    try:
        fn = getattr(requests, method)
        resp = fn(f"{API_BASE}{endpoint}", timeout=30, **kwargs)
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
                    lambda x: ["background-color: #fef2f2"] * len(x), axis=1
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
