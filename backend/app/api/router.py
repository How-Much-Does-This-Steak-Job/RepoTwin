"""API router configuration."""

from fastapi import APIRouter

from app.api import analysis, health, repos

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(repos.router, prefix="/repos", tags=["repositories"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
