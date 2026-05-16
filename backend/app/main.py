"""FastAPI main application for RepoTwin."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api.router import api_router
from app.config import settings
from app.models.database import init_db
from app.utils.errors import AnalysisError, AnalysisNotFoundError, AnalysisTimeoutError, AnalysisValidationError

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Digital Twin for Code Repositories - Powered by IBM Bob",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


# Exception handlers
@app.exception_handler(AnalysisNotFoundError)
async def analysis_not_found_handler(request: Request, exc: AnalysisNotFoundError):
    """Handle AnalysisNotFoundError exceptions."""
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": "ANALYSIS_NOT_FOUND",
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(AnalysisValidationError)
async def analysis_validation_handler(request: Request, exc: AnalysisValidationError):
    """Handle AnalysisValidationError exceptions."""
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": "ANALYSIS_VALIDATION_ERROR",
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(AnalysisTimeoutError)
async def analysis_timeout_handler(request: Request, exc: AnalysisTimeoutError):
    """Handle AnalysisTimeoutError exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "ANALYSIS_TIMEOUT",
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(AnalysisError)
async def analysis_error_handler(request: Request, exc: AnalysisError):
    """Handle generic AnalysisError exceptions."""
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "ANALYSIS_ERROR",
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


# Include API router
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
    }
