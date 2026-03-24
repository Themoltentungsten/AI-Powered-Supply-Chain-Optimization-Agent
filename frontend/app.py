import streamlit as st
import requests
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

API_BASE = "http://localhost:8000/api/v1"

st.set_page_config(
    page_title="Supply Chain Optimization Agent",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Dashboard", "Inventory", "Demand Forecasting", "Purchase Orders", "Risk Alerts", "Savings Report"],
)


def fetch(endpoint: str):
    try:
        resp = requests.get(f"{API_BASE}{endpoint}", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError:
        st.warning("Backend API is not running. Start the FastAPI server first.")
        return None
    except Exception as e:
        st.error(f"API Error: {e}")
        return None


# ── Dashboard ────────────────────────────────────────────────────────────────

if page == "Dashboard":
    st.title("Supply Chain Optimization Dashboard")
    st.markdown("Real-time overview of inventory, forecasting, and supply chain health.")

    col1, col2, col3, col4 = st.columns(4)

    inventory_data = fetch("/inventory")
    if inventory_data:
        total_products = len(inventory_data)
        low_stock = sum(1 for item in inventory_data if item["needs_reorder"])
        total_units = sum(item["quantity_on_hand"] for item in inventory_data)

        col1.metric("Total Products", total_products)
        col2.metric("Low Stock Alerts", low_stock, delta=f"-{low_stock}" if low_stock else "0")
        col3.metric("Total Units in Stock", f"{total_units:,}")
        col4.metric("Active POs", "—")

        st.subheader("Inventory Status Overview")
        df = pd.DataFrame(inventory_data)
        if not df.empty:
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df["product_name"],
                y=df["quantity_on_hand"],
                name="Current Stock",
                marker_color="#2563eb",
            ))
            fig.add_trace(go.Scatter(
                x=df["product_name"],
                y=df["reorder_point"],
                name="Reorder Point",
                mode="lines+markers",
                line=dict(color="#ef4444", dash="dash"),
            ))
            fig.update_layout(
                xaxis_title="Product",
                yaxis_title="Quantity",
                barmode="group",
                template="plotly_white",
                height=450,
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Connect the backend to see live data. Run: `uvicorn backend.app.main:app --reload`")


# ── Inventory ────────────────────────────────────────────────────────────────

elif page == "Inventory":
    st.title("Inventory Management")
    inventory_data = fetch("/inventory")
    if inventory_data:
        df = pd.DataFrame(inventory_data)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.subheader("Products Below Reorder Point")
        low = df[df["needs_reorder"] == True]
        if not low.empty:
            st.dataframe(low, use_container_width=True, hide_index=True)
        else:
            st.success("All products are above reorder point.")
    else:
        st.info("Backend not connected.")


# ── Demand Forecasting ──────────────────────────────────────────────────────

elif page == "Demand Forecasting":
    st.title("Demand Forecasting")
    st.markdown("Prophet-based demand predictions with confidence intervals.")

    products = fetch("/products")
    if products:
        product_options = {p["name"]: p["product_id"] for p in products}
        selected = st.selectbox("Select Product", list(product_options.keys()))
        product_id = product_options[selected]

        sales = fetch(f"/sales-history/{product_id}")
        forecasts = fetch(f"/forecasts/{product_id}")

        if sales:
            st.subheader("Historical Sales")
            sales_df = pd.DataFrame(sales)
            fig = px.line(
                sales_df, x="sale_date", y="quantity_sold",
                title=f"Sales History — {selected}",
                template="plotly_white",
            )
            st.plotly_chart(fig, use_container_width=True)

        if forecasts:
            st.subheader("Demand Forecast")
            fc_df = pd.DataFrame(forecasts)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=fc_df["forecast_date"], y=fc_df["predicted_demand"],
                mode="lines", name="Predicted Demand",
                line=dict(color="#2563eb"),
            ))
            if "lower_bound" in fc_df.columns:
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
            fig.update_layout(template="plotly_white", height=450)
            st.plotly_chart(fig, use_container_width=True)
        elif sales:
            st.info("Forecasts will appear after the Prophet model runs (Day 3).")
    else:
        st.info("Backend not connected.")


# ── Purchase Orders ──────────────────────────────────────────────────────────

elif page == "Purchase Orders":
    st.title("Purchase Orders")
    st.markdown("Auto-generated and manual purchase orders.")

    po_data = fetch("/purchase-orders")
    if po_data:
        df = pd.DataFrame(po_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No purchase orders yet. The agent will generate them on Day 4.")


# ── Risk Alerts ──────────────────────────────────────────────────────────────

elif page == "Risk Alerts":
    st.title("Supply Chain Risk Alerts")
    st.markdown("Risk events identified by RAG pipeline over incidents + live signals.")
    st.info("Risk analysis pipeline will be implemented on Day 3 (RAG) and Day 4 (Agent).")


# ── Savings Report ───────────────────────────────────────────────────────────

elif page == "Savings Report":
    st.title("Monthly Savings Report")
    st.markdown("Projected cost savings from demand forecasting and automated reordering.")
    st.info("Savings report will be populated after the full pipeline runs (Day 5).")


# ── Footer ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("---")
st.sidebar.caption("AI-Powered Supply Chain Optimization Agent v0.1.0")
