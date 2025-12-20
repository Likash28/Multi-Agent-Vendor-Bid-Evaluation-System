"""
Health Check Endpoints
"""

from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check - verify all dependencies are available"""
    # TODO: Add database connectivity check
    return {
        "status": "ready",
        "database": "connected",
    }


@router.get("/live")
async def liveness_check():
    """Liveness check - verify the service is running"""
    return {
        "status": "alive",
    }
