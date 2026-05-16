"""Repository Pydantic schemas."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class RepositoryBase(BaseModel):
    """Base repository schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    url: HttpUrl


class RepositoryCreate(RepositoryBase):
    """Repository creation schema."""
    pass


class RepositoryUpdate(BaseModel):
    """Repository update schema."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)


class RepositoryLanguage(BaseModel):
    """Repository language statistics."""
    name: str
    files: int
    lines: int
    percentage: float


class Repository(RepositoryBase):
    """Repository response schema."""
    id: UUID
    status: str
    default_branch: str = "main"
    total_files: int = 0
    total_lines: int = 0
    languages: Optional[List[RepositoryLanguage]] = None
    created_at: datetime
    updated_at: datetime
    last_synced_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class RepositoryFileTree(BaseModel):
    """Repository file tree schema."""
    path: str
    files: List[Dict[str, Any]]
    directories: List[str]


class RepositoryList(BaseModel):
    """Repository list response."""
    items: List[Repository]
    total: int
    skip: int
    limit: int
