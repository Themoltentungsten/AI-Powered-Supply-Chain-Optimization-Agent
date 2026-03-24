"""
Generate the system architecture diagram as a PNG image.

Run: python docs/architecture_diagram.py
Outputs: docs/architecture_diagram.png
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import os

fig, ax = plt.subplots(1, 1, figsize=(18, 13))
ax.set_xlim(0, 18)
ax.set_ylim(0, 13)
ax.axis("off")
fig.patch.set_facecolor("#f8fafc")

BLUE = "#2563eb"
DARK = "#1e293b"
RED = "#ef4444"
GREEN = "#16a34a"
PURPLE = "#7c3aed"
ORANGE = "#ea580c"
LIGHT_BLUE = "#dbeafe"
LIGHT_GREEN = "#dcfce7"
LIGHT_PURPLE = "#ede9fe"
LIGHT_ORANGE = "#fff7ed"
LIGHT_RED = "#fef2f2"
GRAY = "#f1f5f9"

# ── Title
ax.text(9, 12.5, "AI-Powered Supply Chain Optimization Agent",
        ha="center", va="center", fontsize=18, fontweight="bold", color=DARK)
ax.text(9, 12.1, "System Architecture",
        ha="center", va="center", fontsize=12, color="#64748b")

# ── Layer 1: Streamlit Dashboard (top)
dash_box = FancyBboxPatch((1, 9.8), 16, 2,
                           boxstyle="round,pad=0.15", facecolor=LIGHT_BLUE,
                           edgecolor=BLUE, linewidth=2)
ax.add_patch(dash_box)
ax.text(9, 11.4, "STREAMLIT DASHBOARD (Frontend)", ha="center",
        fontsize=13, fontweight="bold", color=BLUE)

dash_items = [
    (3, 10.5, "Inventory\nOverview"),
    (7, 10.5, "Forecasting\nGraphs (Plotly)"),
    (11, 10.5, "Risk\nAlerts"),
    (15, 10.5, "Purchase Orders &\nSavings Report"),
]
for x, y, label in dash_items:
    box = FancyBboxPatch((x - 1.4, y - 0.4), 2.8, 0.8,
                          boxstyle="round,pad=0.1", facecolor="white",
                          edgecolor=BLUE, linewidth=1)
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=8, color=DARK)

# ── Arrow: Dashboard -> Backend
ax.annotate("", xy=(9, 9.0), xytext=(9, 9.7),
            arrowprops=dict(arrowstyle="->", color=DARK, lw=2))
ax.text(9.5, 9.35, "REST API", fontsize=8, color="#64748b")

# ── Layer 2: FastAPI + LangChain Agent (middle)
api_box = FancyBboxPatch((1, 5.5), 16, 3.4,
                          boxstyle="round,pad=0.15", facecolor=LIGHT_PURPLE,
                          edgecolor=PURPLE, linewidth=2)
ax.add_patch(api_box)
ax.text(9, 8.5, "FASTAPI BACKEND + LANGCHAIN ReAct AGENT", ha="center",
        fontsize=13, fontweight="bold", color=PURPLE)

agent_box = FancyBboxPatch((2, 7.0), 14, 1.2,
                            boxstyle="round,pad=0.1", facecolor="white",
                            edgecolor=PURPLE, linewidth=1.5, linestyle="--")
ax.add_patch(agent_box)
ax.text(9, 7.9, "LangChain ReAct Agent (GPT-4o) — Chain-of-Thought Reasoning",
        ha="center", fontsize=9, fontweight="bold", color=PURPLE)

tools = [
    (3.5, 7.2, "Query\nInventory", GREEN),
    (7, 7.2, "Run\nForecast", BLUE),
    (10.5, 7.2, "Generate\nPO", ORANGE),
    (14, 7.2, "Search Risk\nIntelligence", RED),
]
for x, y, label, color in tools:
    box = FancyBboxPatch((x - 1.2, y - 0.35), 2.4, 0.7,
                          boxstyle="round,pad=0.08", facecolor="white",
                          edgecolor=color, linewidth=1.5)
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=7.5, color=color, fontweight="bold")

services = [
    (3.5, 6.1, "Inventory\nService", GREEN),
    (7, 6.1, "Prophet\nForecast Engine", BLUE),
    (10.5, 6.1, "PO\nGenerator", ORANGE),
    (14, 6.1, "RAG Pipeline\n(ChromaDB)", RED),
]
for x, y, label, color in services:
    box = FancyBboxPatch((x - 1.3, y - 0.35), 2.6, 0.7,
                          boxstyle="round,pad=0.08", facecolor="white",
                          edgecolor=color, linewidth=1)
    ax.add_patch(box)
    ax.text(x, y, label, ha="center", va="center", fontsize=7.5, color=DARK)

# ── Arrows between tools and services
for x, _, _, _ in tools:
    ax.annotate("", xy=(x, 6.5), xytext=(x, 6.85),
                arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=1.2))

# ── Arrow: Backend -> Data
ax.annotate("", xy=(9, 4.5), xytext=(9, 5.4),
            arrowprops=dict(arrowstyle="->", color=DARK, lw=2))

# ── Layer 3: Data Layer (bottom)
data_box = FancyBboxPatch((1, 1.0), 16, 3.4,
                           boxstyle="round,pad=0.15", facecolor=LIGHT_GREEN,
                           edgecolor=GREEN, linewidth=2)
ax.add_patch(data_box)
ax.text(9, 4.0, "DATA LAYER", ha="center",
        fontsize=13, fontweight="bold", color=GREEN)

# PostgreSQL
pg_box = FancyBboxPatch((1.8, 1.4), 4.5, 2.2,
                          boxstyle="round,pad=0.1", facecolor="white",
                          edgecolor=GREEN, linewidth=1)
ax.add_patch(pg_box)
ax.text(4.05, 3.2, "PostgreSQL", ha="center", fontsize=10, fontweight="bold", color=GREEN)
pg_tables = ["products", "inventory", "sales_history", "suppliers", "purchase_orders"]
for i, t in enumerate(pg_tables):
    ax.text(4.05, 2.8 - i * 0.28, f"• {t}", ha="center", fontsize=7.5, color=DARK)

# External APIs
api_ext_box = FancyBboxPatch((7.0, 1.4), 4, 2.2,
                              boxstyle="round,pad=0.1", facecolor="white",
                              edgecolor=ORANGE, linewidth=1)
ax.add_patch(api_ext_box)
ax.text(9, 3.2, "External APIs", ha="center", fontsize=10, fontweight="bold", color=ORANGE)
ext_items = ["OpenWeatherMap", "News Feeds", "Commodity Prices"]
for i, t in enumerate(ext_items):
    ax.text(9, 2.7 - i * 0.35, f"• {t}", ha="center", fontsize=8, color=DARK)

# Document Store
doc_box = FancyBboxPatch((11.7, 1.4), 4.5, 2.2,
                          boxstyle="round,pad=0.1", facecolor="white",
                          edgecolor=RED, linewidth=1)
ax.add_patch(doc_box)
ax.text(13.95, 3.2, "Document Store (RAG)", ha="center", fontsize=10, fontweight="bold", color=RED)
doc_items = ["Historical Incidents", "Supplier Reports", "Risk Embeddings"]
for i, t in enumerate(doc_items):
    ax.text(13.95, 2.7 - i * 0.35, f"• {t}", ha="center", fontsize=8, color=DARK)

# ── Pipeline flow at bottom
ax.text(9, 0.5,
        "Pipeline:  Data Integration  →  Demand Forecasting  →  Agent Orchestration  →  Streamlit Dashboard",
        ha="center", va="center", fontsize=10, fontweight="bold", color=DARK,
        bbox=dict(boxstyle="round,pad=0.3", facecolor="#f1f5f9", edgecolor="#cbd5e1"))

output_path = os.path.join(os.path.dirname(__file__), "architecture_diagram.png")
plt.tight_layout()
plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="#f8fafc")
print(f"Architecture diagram saved to: {output_path}")
