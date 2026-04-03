# ═══════════════════════════════════════════════════════════════════════
#  DAY 3: Risk analysis endpoint — RAG search over supply-chain events
# ═══════════════════════════════════════════════════════════════════════

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.schema import RiskEvent
from ..services.risk_rag_service import search_risks

router = APIRouter(tags=["Risk Analysis"])


# ── DAY 3 START: List all risk events ────────────────────────────────
@router.get("/risks")
def list_risk_events(db: Session = Depends(get_db)):
    rows = db.execute(
        select(RiskEvent).order_by(RiskEvent.event_date.desc())
    ).scalars().all()
    return [
        {
            "event_id": r.event_id,
            "event_type": r.event_type,
            "severity": r.severity,
            "description": r.description,
            "affected_suppliers": r.affected_suppliers,
            "affected_region": r.affected_region,
            "event_date": str(r.event_date),
            "resolved": r.resolved,
            "source": r.source,
        }
        for r in rows
    ]
# ── DAY 3 END (list) ────────────────────────────────────────────────


# ── DAY 3 START: Semantic risk search via RAG ────────────────────────
@router.get("/risks/search")
def search_risk_events(
    q: str = Query(..., min_length=2, description="Natural-language risk query"),
    n: int = Query(default=5, ge=1, le=20),
):
    return search_risks(query=q, n_results=n)
# ── DAY 3 END (search) ──────────────────────────────────────────────
