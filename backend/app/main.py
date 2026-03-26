# ═══════════════════════════════════════════════════════════════════════
#  DAY 1: FastAPI app creation, CORS, initial routers
#  DAY 2: Added weather router, sync lifespan
#  DAY 3: Added risk router, RAG index init at startup
#  DAY 4: Added agent orchestration router
# ═══════════════════════════════════════════════════════════════════════

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .config import get_settings
from .database import init_db, SessionLocal

# ── DAY 1 START: Import routers ──────────────────────────────────────
from .routers import inventory, forecasting, purchase_orders, health
# ── DAY 1 END ────────────────────────────────────────────────────────

# ── DAY 2 START: Weather router ──────────────────────────────────────
from .routers import weather
# ── DAY 2 END ────────────────────────────────────────────────────────

# ── DAY 3 START: Risk router + RAG init helper ──────────────────────
from .routers import risk
from .routers import data_manager
from .models.schema import RiskEvent
from .services.risk_rag_service import init_risk_index
# ── DAY 3 END ────────────────────────────────────────────────────────

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── DAY 1: Create DB tables ──────────────────────────────────────
    init_db()

    # ── DAY 3: Index risk events into ChromaDB for RAG search ────────
    db = SessionLocal()
    try:
        rows = db.execute(select(RiskEvent)).scalars().all()
        if rows:
            events = [
                {
                    "event_id": r.event_id,
                    "event_type": r.event_type,
                    "severity": r.severity,
                    "description": r.description,
                    "affected_suppliers": r.affected_suppliers,
                    "affected_region": r.affected_region,
                    "event_date": str(r.event_date),
                }
                for r in rows
            ]
            init_risk_index(events)
    finally:
        db.close()

    yield


# ── DAY 1 START: FastAPI app ─────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Supply Chain Optimization Agent — REST API",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(inventory.router, prefix="/api/v1")
app.include_router(forecasting.router, prefix="/api/v1")
app.include_router(purchase_orders.router, prefix="/api/v1")
# ── DAY 1 END ────────────────────────────────────────────────────────

# ── DAY 2 START: Register weather router ─────────────────────────────
app.include_router(weather.router, prefix="/api/v1")
# ── DAY 2 END ────────────────────────────────────────────────────────

# ── DAY 3 START: Register risk router ────────────────────────────────
app.include_router(risk.router, prefix="/api/v1")
# ── DAY 3 END ────────────────────────────────────────────────────────

app.include_router(data_manager.router, prefix="/api/v1")

# ── DAY 4 START: Register agent orchestration router ──────────────────
from .routers import agent as agent_router
app.include_router(agent_router.router, prefix="/api/v1")
# ── DAY 4 END ────────────────────────────────────────────────────────
