# ═══════════════════════════════════════════════════════════════════════
#  DAY 1: Health-check endpoint
# ═══════════════════════════════════════════════════════════════════════

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


# ── DAY 1 START: Basic health check ─────────────────────────────────
@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Supply Chain Optimization Agent API",
        "version": "0.1.0",
    }
# ── DAY 1 END ────────────────────────────────────────────────────────
