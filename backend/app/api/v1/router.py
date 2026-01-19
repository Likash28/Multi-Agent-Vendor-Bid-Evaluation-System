"""
API v1 Router - Aggregates all endpoint routers
"""

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.evaluations import router as evaluations_router
from app.api.v1.documents import router as documents_router
from app.api.v1.vendors import router as vendors_router
from app.api.v1.admin import router as admin_router
from app.api.v1.health import router as health_router
from app.api.v1.reports import router as reports_router

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["Authentication"])
api_router.include_router(evaluations_router, prefix="/evaluations", tags=["Evaluations"])
api_router.include_router(documents_router, prefix="/documents", tags=["Documents"])
api_router.include_router(vendors_router, prefix="/vendors", tags=["Vendors"])
api_router.include_router(admin_router, prefix="/admin", tags=["Admin"])
api_router.include_router(health_router, prefix="/health", tags=["Health"])
api_router.include_router(reports_router, prefix="/reports", tags=["Reports"])
