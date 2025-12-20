"""
FastAPI Application Entry Point
Main application with CORS, middleware, and lifespan management
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.dependencies import init_db, close_db
from app.core.middleware import SecurityHeadersMiddleware
from app.core.exceptions import setup_exception_handlers
from app.api.v1.router import api_router
from app.api.websocket import websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    print(f"Starting {settings.APP_NAME}...")
    await init_db()
    print("Database initialized")

    yield

    # Shutdown
    print("Shutting down...")
    await close_db()
    print("Database connections closed")


# Create FastAPI application
app = FastAPI(
    title="GovProcure API",
    description="Multi-Agent Vendor Bid Evaluation System",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Headers Middleware
app.add_middleware(SecurityHeadersMiddleware)

# Include routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(websocket_router, prefix="/ws")

# Setup exception handlers
setup_exception_handlers(app)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/api/docs",
        "health": "/health",
    }
