"""Repository service."""

import json
import logging
import shutil
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from git import Repo
from git.exc import GitCommandError

from app.config import settings
from app.core.code_parser import code_parser
from app.core.impact_engine import impact_engine
from app.redis import get_store
from app.schemas.repository import RepositoryCreate, RepositoryUpdate

logger = logging.getLogger(__name__)


class RepositoryService:
    """Service for repository operations."""
    
    # Redis key patterns
    REPO_KEY_PREFIX = "repo"
    REPO_LIST_KEY = "repos:list"
    TTL_SECONDS = 86400  # 24 hours TTL for repository metadata
    
    def __init__(self):
        """Initialize repository service."""
        self.storage_path = Path(settings.git_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self._store = None
    
    async def _get_store(self):
        """Get store instance (lazy initialization)."""
        if self._store is None:
            self._store = await get_store()
        return self._store
    
    def _get_repo_key(self, repo_id: UUID) -> str:
        """Generate Redis key for repository data."""
        return f"{self.REPO_KEY_PREFIX}:{str(repo_id)}:data"
    
    async def set_repo(self, repo_id: UUID, repo_data: dict) -> None:
        """Store repository metadata in Redis.
        
        Args:
            repo_id: Repository UUID
            repo_data: Repository metadata dictionary
        """
        store = await self._get_store()
        repo_key = self._get_repo_key(repo_id)
        await store.set(repo_key, json.dumps(repo_data), ttl=self.TTL_SECONDS)
        logger.debug(f"Stored repository {repo_id} in Redis")
    
    async def get_repo(self, repo_id: UUID) -> Optional[dict]:
        """Get repository metadata from Redis.
        
        Args:
            repo_id: Repository UUID
            
        Returns:
            Repository data dict if found, None otherwise
        """
        store = await self._get_store()
        repo_key = self._get_repo_key(repo_id)
        data = await store.get(repo_key)
        
        if data is None:
            return None
        
        try:
            return json.loads(data)
        except Exception as e:
            logger.error(f"Failed to parse repository {repo_id}: {e}")
            return None
    
    async def list_repos(self) -> List[dict]:
        """List all repositories from Redis.
        
        Returns:
            List of repository data dicts
        """
        store = await self._get_store()
        pattern = f"{self.REPO_KEY_PREFIX}:*:data"
        keys = await store.keys(pattern)
        
        repos = []
        for key in keys:
            try:
                data = await store.get(key)
                if data:
                    repos.append(json.loads(data))
            except Exception as e:
                logger.error(f"Failed to parse repository from key {key}: {e}")
                continue
        
        return repos
    
    async def delete_repo(self, repo_id: UUID) -> bool:
        """Delete repository metadata from Redis.
        
        Args:
            repo_id: Repository UUID
            
        Returns:
            True if deleted, False if not found
        """
        store = await self._get_store()
        repo_key = self._get_repo_key(repo_id)
        
        if not await store.exists(repo_key):
            return False
        
        await store.delete(repo_key)
        logger.debug(f"Deleted repository {repo_id} from Redis")
        return True
    
    def _get_repo_path(self, repo_id: UUID) -> Path:
        """Get local path for repository."""
        return self.storage_path / str(repo_id)
    
    async def create_repository(self, data: RepositoryCreate, skip_clone: bool = False) -> dict:
        """Create and clone a repository.
        
        Args:
            data: Repository creation data
            skip_clone: If True, create mock repo without cloning (for demo)
            
        Returns:
            Repository data dict
        """
        from uuid import uuid4
        
        repo_id = uuid4()
        
        # If local_path is provided, use it directly
        if hasattr(data, 'local_path') and data.local_path:
            local_path = Path(data.local_path)
            if not local_path.exists():
                raise ValueError(f"Local path does not exist: {local_path}")
            
            # Get repository info from existing path
            total_files = sum(1 for _ in local_path.rglob('*') if _.is_file())
            languages = self._detect_languages(local_path)
            
            repo_data = {
                'id': str(repo_id),
                'name': data.name,
                'url': str(data.url),
                'description': data.description,
                'status': 'ready',
                'default_branch': data.branch if hasattr(data, 'branch') else 'main',
                'total_files': total_files,
                'local_path': str(local_path),
                'languages': languages,
            }
            
            await self.set_repo(repo_id, repo_data)
            logger.info(f"Created repository {repo_id} from local path")
            return repo_data
        
        # If skip_clone is True, create mock repository for demo
        if skip_clone:
            return await self._create_mock_repository(repo_id, data)
        
        local_path = self._get_repo_path(repo_id)
        
        try:
            # Clone repository
            logger.info(f"Cloning {data.url} to {local_path}")
            repo = Repo.clone_from(
                str(data.url),
                local_path,
                branch=data.branch if hasattr(data, 'branch') else 'main',
                depth=1,
            )
            
            # Get repository info
            total_files = sum(1 for _ in local_path.rglob('*') if _.is_file())
            
            # Detect languages
            languages = self._detect_languages(local_path)
            
            # Build repository data
            repo_data = {
                'id': str(repo_id),
                'name': data.name,
                'url': str(data.url),
                'description': data.description,
                'status': 'ready',
                'default_branch': repo.active_branch.name,
                'total_files': total_files,
                'local_path': str(local_path),
                'languages': languages,
            }
            
            # Store metadata in Redis
            await self.set_repo(repo_id, repo_data)
            logger.info(f"Created and stored repository {repo_id}")
            
            return repo_data
            
        except GitCommandError as e:
            logger.error(f"Git clone failed: {e}")
            # Clean up if clone failed
            if local_path.exists():
                shutil.rmtree(local_path)
            raise
        except Exception as e:
            logger.error(f"Repository creation failed: {e}")
            if local_path.exists():
                shutil.rmtree(local_path)
            raise
    
    async def _create_mock_repository(self, repo_id: UUID, data: RepositoryCreate) -> dict:
        """Create a mock repository for demo purposes.
        
        Args:
            repo_id: Repository UUID
            data: Repository creation data
            
        Returns:
            Mock repository data dict
        """
        repo_data = {
            'id': str(repo_id),
            'name': data.name,
            'url': str(data.url),
            'description': data.description,
            'status': 'ready',
            'default_branch': data.branch if hasattr(data, 'branch') else 'main',
            'total_files': 387,
            'total_lines': 45230,
            'local_path': None,
            'languages': [
                {'name': 'Kotlin', 'files': 120, 'lines': 15000, 'percentage': 33.1},
                {'name': 'Java', 'files': 85, 'lines': 12000, 'percentage': 26.5},
                {'name': 'XML', 'files': 95, 'lines': 10000, 'percentage': 22.1},
                {'name': 'Python', 'files': 45, 'lines': 5000, 'percentage': 11.0},
                {'name': 'JavaScript', 'files': 42, 'lines': 3230, 'percentage': 7.3},
            ],
        }
        
        await self.set_repo(repo_id, repo_data)
        logger.info(f"Created mock repository {repo_id}")
        return repo_data
    
    def _detect_languages(self, repo_path: Path) -> List[dict]:
        """Detect programming languages in repository.
        
        Args:
            repo_path: Repository path
            
        Returns:
            List of language info dicts
        """
        extensions = {}
        total_lines = 0
        
        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and '.git' not in str(file_path):
                ext = file_path.suffix.lower()
                if ext:
                    try:
                        lines = len(file_path.read_text().splitlines())
                        extensions[ext] = extensions.get(ext, 0) + lines
                        total_lines += lines
                    except:
                        pass
        
        # Map extensions to languages
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cpp': 'C++',
            '.c': 'C',
            '.h': 'C/C++',
            '.hpp': 'C++',
        }
        
        languages = []
        for ext, lines in sorted(extensions.items(), key=lambda x: -x[1]):
            if ext in lang_map:
                languages.append({
                    'name': lang_map[ext],
                    'files': lines,  # Approximate
                    'lines': lines,
                    'percentage': round(lines / total_lines * 100, 2) if total_lines > 0 else 0,
                })
        
        return languages[:5]  # Top 5 languages
    
    async def get_repository(self, repo_id: UUID) -> Optional[dict]:
        """Get repository by ID.
        
        First checks Redis for metadata, then falls back to filesystem.
        
        Args:
            repo_id: Repository UUID
            
        Returns:
            Repository data or None
        """
        # Try to get from Redis first
        repo_data = await self.get_repo(repo_id)
        if repo_data is not None:
            return repo_data
        
        # Fallback to filesystem lookup
        local_path = self._get_repo_path(repo_id)
        
        if not local_path.exists():
            return None
        
        # Get basic info from filesystem - minimal fallback
        total_files = sum(1 for _ in local_path.rglob('*') if _.is_file())
        languages = self._detect_languages(local_path)
        
        fallback_data = {
            'id': str(repo_id),
            'name': 'Unknown Repository',
            'url': '',
            'description': None,
            'status': 'ready',
            'default_branch': 'main',
            'total_files': total_files,
            'local_path': str(local_path),
            'languages': languages,
        }
        
        # Store the fallback data in Redis for future lookups
        await self.set_repo(repo_id, fallback_data)
        logger.info(f"Created fallback metadata for repository {repo_id}")
        
        return fallback_data
    
    async def delete_repository(self, repo_id: UUID) -> bool:
        """Delete repository.
        
        Removes both from filesystem and Redis.
        
        Args:
            repo_id: Repository UUID
            
        Returns:
            True if deleted from filesystem or Redis
        """
        deleted = False
        
        # Delete from filesystem
        local_path = self._get_repo_path(repo_id)
        if local_path.exists():
            shutil.rmtree(local_path)
            deleted = True
            logger.info(f"Deleted repository {repo_id} from filesystem")
        
        # Delete from Redis
        redis_deleted = await self.delete_repo(repo_id)
        if redis_deleted:
            deleted = True
            logger.info(f"Deleted repository {repo_id} from Redis")
        
        return deleted
    
    async def list_repositories(self) -> List[dict]:
        """List all repositories.
        
        Returns:
            List of repository data dicts from Redis
        """
        repos = await self.list_repos()
        logger.info(f"Listed {len(repos)} repositories from Redis")
        return repos
    
    async def get_file_tree(self, repo_id: UUID, path: str = "") -> dict:
        """Get repository file tree.
        
        Args:
            repo_id: Repository UUID
            path: Subdirectory path
            
        Returns:
            File tree structure
        """
        local_path = self._get_repo_path(repo_id)
        target_path = local_path / path if path else local_path
        
        if not target_path.exists():
            return {'path': path, 'files': [], 'directories': []}
        
        files = []
        directories = []
        
        for item in sorted(target_path.iterdir()):
            if item.name.startswith('.') and item.name != '.github':
                continue
            
            if item.is_dir():
                directories.append(item.name)
            else:
                files.append({
                    'name': item.name,
                    'size': item.stat().st_size,
                    'extension': item.suffix,
                })
        
        return {
            'path': path or '/',
            'files': files,
            'directories': directories,
        }
    
    async def parse_repository(self, repo_id: UUID) -> List[dict]:
        """Parse all files in repository.
        
        Args:
            repo_id: Repository UUID
            
        Returns:
            List of parse results
        """
        local_path = self._get_repo_path(repo_id)
        
        if not local_path.exists():
            return []
        
        results = code_parser.parse_directory(str(local_path))
        
        return [
            {
                'file_path': r.file_path,
                'language': r.language,
                'functions': [f.name for f in r.functions],
                'classes': [c.name for c in r.classes],
                'imports': [i.module for i in r.imports],
            }
            for r in results
        ]


# Singleton instance
repo_service = RepositoryService()
