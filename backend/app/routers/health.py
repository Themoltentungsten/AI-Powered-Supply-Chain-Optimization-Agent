from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Supply Chain Optimization Agent API",
        "version": "0.1.0",
    }
