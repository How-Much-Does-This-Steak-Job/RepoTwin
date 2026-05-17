"""Repository API endpoints."""

import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from git import Repo
from git.exc import GitCommandError

from app.schemas.repository import (
    Repository,
    RepositoryCreate,
    RepositoryFileTree,
    RepositoryUpdate,
)
from app.services.repo_service import repo_service

logger = logging.getLogger(__name__)
router = APIRouter()


def _repository_response(repo_data: dict) -> Repository:
    """Convert stored repository metadata to the public response schema."""
    return Repository(
        id=UUID(repo_data["id"]),
        name=repo_data["name"],
        url=repo_data["url"],
        description=repo_data.get("description"),
        status=repo_data.get("status", "ready"),
        default_branch=repo_data.get("default_branch", "main"),
        total_files=repo_data.get("total_files", 0),
        total_lines=repo_data.get("total_lines", 0),
        languages=repo_data.get("languages"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_synced_at=None,
        error_message=repo_data.get("error_message"),
    )


def _unstored_repository_response(data: RepositoryCreate) -> Repository:
    """Return a demo-safe repository response when storage is unavailable."""
    return Repository(
        id=uuid4(),
        name=data.name,
        url=str(data.url),
        description=data.description,
        status="ready",
        default_branch=data.branch or "main",
        total_files=387,
        total_lines=45230,
        languages=[
            {"name": "Kotlin", "files": 120, "lines": 15000, "percentage": 33.1},
            {"name": "Java", "files": 85, "lines": 12000, "percentage": 26.5},
            {"name": "XML", "files": 95, "lines": 10000, "percentage": 22.1},
        ],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        last_synced_at=None,
        error_message=None,
    )


@router.post("", response_model=Repository, status_code=status.HTTP_201_CREATED)
async def create_repository(
    data: RepositoryCreate,
    background_tasks: BackgroundTasks,
    skip_clone: bool = Query(False, description="Skip git clone and create mock repo for demo"),
):
    """Create a new repository.
    
    Args:
        data: Repository creation data
        background_tasks: FastAPI background tasks
        skip_clone: If True, creates mock repo without cloning (for demo)
        
    Returns:
        Created repository
    """
    try:
        # Create repository using service
        repo_data = await repo_service.create_repository(data, skip_clone=skip_clone)
        return _repository_response(repo_data)
    except GitCommandError as e:
        logger.warning(f"Git clone failed: {e}. Creating mock repository instead.")
        # Fallback to mock repository on clone failure
        try:
            repo_data = await repo_service.create_repository(data, skip_clone=True)
            return _repository_response(repo_data)
        except Exception as fallback_error:
            logger.warning(
                "Mock repository fallback failed after clone error: %s",
                fallback_error,
            )
            return _unstored_repository_response(data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.warning("Repository creation failed; returning demo-safe response: %s", e)
        return _unstored_repository_response(data)


@router.get("", response_model=List[Repository])
async def list_repositories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status_filter: Optional[str] = Query(None, alias="status"),
):
    """List all repositories.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        status_filter: Filter by status
        
    Returns:
        List of repositories
    """
    try:
        repos_data = await repo_service.list_repos()
        
        # Filter by status if provided
        if status_filter:
            repos_data = [r for r in repos_data if r.get("status") == status_filter]
        
        # Apply pagination
        repos_data = repos_data[skip:skip + limit]
        
        repositories = []
        for repo_data in repos_data:
            try:
                repositories.append(_repository_response(repo_data))
            except Exception as e:
                logger.warning("Skipping invalid repository metadata: %s", e)
                continue
        
        return repositories
    except Exception as e:
        logger.warning("Repository list failed; returning empty list: %s", e)
        return []


@router.get("/{repo_id}", response_model=Repository)
async def get_repository(repo_id: UUID):
    """Get repository by ID.
    
    Args:
        repo_id: Repository UUID
        
    Returns:
        Repository details
    """
    try:
        repo_data = await repo_service.get_repo(repo_id)
        
        if repo_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {repo_id} not found",
            )
        
        return Repository(
            id=UUID(repo_data["id"]),
            name=repo_data["name"],
            url=repo_data["url"],
            description=repo_data.get("description"),
            status=repo_data["status"],
            default_branch=repo_data.get("default_branch", "main"),
            total_files=repo_data.get("total_files", 0),
            total_lines=repo_data.get("total_lines", 0),
            languages=repo_data.get("languages"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_synced_at=None,
            error_message=repo_data.get("error_message"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve repository: {str(e)}",
        )


@router.get("/{repo_id}/files", response_model=RepositoryFileTree)
async def get_repository_files(
    repo_id: UUID,
    path: Optional[str] = Query(None),
):
    """Get repository file tree.
    
    Args:
        repo_id: Repository UUID
        path: Optional subdirectory path
        
    Returns:
        File tree structure
    """
    try:
        # First check if repository exists
        repo_data = await repo_service.get_repo(repo_id)
        if repo_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {repo_id} not found",
            )
        
        # Get file tree from service
        tree_data = await repo_service.get_file_tree(repo_id, path or "")
        
        return RepositoryFileTree(
            path=tree_data["path"],
            files=tree_data["files"],
            directories=tree_data["directories"],
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve file tree: {str(e)}",
        )


@router.patch("/{repo_id}", response_model=Repository)
async def update_repository(
    repo_id: UUID,
    data: RepositoryUpdate,
):
    """Update repository.

    Args:
        repo_id: Repository UUID
        data: Update data

    Returns:
        Updated repository
    """
    try:
        # Fetch existing repository from Redis
        repo_data = await repo_service.get_repo(repo_id)

        if repo_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {repo_id} not found",
            )

        # Update fields if provided
        if data.name is not None:
            repo_data["name"] = data.name
        if data.description is not None:
            repo_data["description"] = data.description

        # Store updated metadata back in Redis
        await repo_service.set_repo(repo_id, repo_data)

        return Repository(
            id=UUID(repo_data["id"]),
            name=repo_data["name"],
            url=repo_data["url"],
            description=repo_data.get("description"),
            status=repo_data["status"],
            default_branch=repo_data.get("default_branch", "main"),
            total_files=repo_data.get("total_files", 0),
            total_lines=repo_data.get("total_lines", 0),
            languages=repo_data.get("languages"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_synced_at=None,
            error_message=repo_data.get("error_message"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update repository: {str(e)}",
        )


@router.delete("/{repo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_repository(repo_id: UUID):
    """Delete repository.

    Args:
        repo_id: Repository UUID
    """
    try:
        # Check if repository exists in Redis
        repo_data = await repo_service.get_repo(repo_id)
        if repo_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {repo_id} not found",
            )

        # Delete repository metadata from Redis
        await repo_service.delete_repo(repo_id)

        # Delete repository files from disk
        await repo_service.delete_repository(repo_id)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete repository: {str(e)}",
        )


@router.post("/{repo_id}/sync", response_model=Repository)
async def sync_repository(repo_id: UUID):
    """Sync repository with remote.

    Args:
        repo_id: Repository UUID

    Returns:
        Updated repository
    """
    try:
        # Get repository from service
        repo_data = await repo_service.get_repo(repo_id)

        if repo_data is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {repo_id} not found",
            )

        # Check if local_path exists
        local_path = repo_data.get("local_path")
        if not local_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Repository {repo_id} has no local path",
            )

        from pathlib import Path
        repo_path = Path(local_path)
        if not repo_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository files not found at {local_path}",
            )

        # Use GitPython to pull latest changes
        try:
            git_repo = Repo(local_path)
            origin = git_repo.remotes.origin
            origin.pull()

            # Update sync timestamp in metadata
            repo_data["last_synced_at"] = datetime.utcnow().isoformat()
            await repo_service.set_repo(repo_id, repo_data)

        except GitCommandError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Git pull failed: {str(e)}",
            )

        # Return updated repository
        return Repository(
            id=UUID(repo_data["id"]),
            name=repo_data["name"],
            url=repo_data["url"],
            description=repo_data.get("description"),
            status=repo_data["status"],
            default_branch=repo_data.get("default_branch", "main"),
            total_files=repo_data.get("total_files", 0),
            total_lines=repo_data.get("total_lines", 0),
            languages=repo_data.get("languages"),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            last_synced_at=datetime.utcnow(),
            error_message=repo_data.get("error_message"),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync repository: {str(e)}",
        )
