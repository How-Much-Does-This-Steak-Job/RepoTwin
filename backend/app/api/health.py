"""Health check endpoints."""

from fastapi import APIRouter, status

router = APIRouter()


@router.get("", status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check."""
    return {"status": "ok", "service": "repotwin"}


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """Readiness probe for Kubernetes."""
    return {"ready": True}


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """Liveness probe for Kubernetes."""
    return {"alive": True}
