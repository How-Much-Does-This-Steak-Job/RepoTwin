"""Database models and connection."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.config import settings


class Base(AsyncAttrs, DeclarativeBase):
    """Base model with async support."""
    pass


class RepositoryStatus(str, Enum):
    """Repository processing status."""
    PENDING = "pending"
    CLONING = "cloning"
    PARSING = "parsing"
    READY = "ready"
    ERROR = "error"


class AnalysisStatus(str, Enum):
    """Analysis processing status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RepositoryModel(Base):
    """Repository database model."""
    
    __tablename__ = "repositories"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(50), default=RepositoryStatus.PENDING)
    
    # Storage
    local_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    default_branch: Mapped[str] = mapped_column(String(100), default="main")
    
    # Metadata
    total_files: Mapped[int] = mapped_column(default=0)
    total_lines: Mapped[int] = mapped_column(default=0)
    languages: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class AnalysisModel(Base):
    """Analysis database model."""
    
    __tablename__ = "analyses"
    
    id: Mapped[UUID] = mapped_column(PGUUID, primary_key=True, default=uuid4)
    repo_id: Mapped[UUID] = mapped_column(PGUUID, nullable=False)
    
    # Input
    change_description: Mapped[str] = mapped_column(Text, nullable=False)
    target_branch: Mapped[str] = mapped_column(String(100), default="main")
    selected_files: Mapped[Optional[list]] = mapped_column(JSONB, nullable=True)
    
    # Status
    status: Mapped[str] = mapped_column(String(50), default=AnalysisStatus.PENDING)
    progress_percent: Mapped[int] = mapped_column(default=0)
    current_step: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Results
    results: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


# Database engine
engine = create_async_engine(
    settings.async_database_url,
    pool_size=settings.database_pool_size,
    max_overflow=settings.database_max_overflow,
    echo=settings.debug,
)

# Session factory
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Initialize database tables.
    
    Note: Database is optional for MVP. If connection fails,
    the app will continue using Redis/memory storage.
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.warning(f"Database connection failed (optional for MVP): {e}")
        logger.info("Continuing without database - using Redis/memory storage only")


async def get_db():
    """Get database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
