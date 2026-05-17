"""API router configuration."""

from fastapi import APIRouter

from app.api import analysis, health, repos, shadow_pr

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(repos.router, prefix="/repos", tags=["repositories"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(shadow_pr.router, prefix="/analysis", tags=["shadow-pr"])

# AGENTS.md compliance: Add /analyze and /demo endpoints
# This allows POST /api/analyze and GET /api/demo/{id}/results to work
api_router.include_router(
    analysis.simple_router,
    prefix="",
    tags=["demo"],
)
