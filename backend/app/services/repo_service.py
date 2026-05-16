"""Repository service."""

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
from app.schemas.repository import RepositoryCreate, RepositoryUpdate

logger = logging.getLogger(__name__)


class RepositoryService:
    """Service for repository operations."""
    
    def __init__(self):
        """Initialize repository service."""
        self.storage_path = Path(settings.git_storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def _get_repo_path(self, repo_id: UUID) -> Path:
        """Get local path for repository."""
        return self.storage_path / str(repo_id)
    
    async def create_repository(self, data: RepositoryCreate) -> dict:
        """Create and clone a repository.
        
        Args:
            data: Repository creation data
            
        Returns:
            Repository data dict
        """
        from uuid import uuid4
        
        repo_id = uuid4()
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
            
            return {
                'id': repo_id,
                'name': data.name,
                'url': str(data.url),
                'description': data.description,
                'status': 'ready',
                'default_branch': repo.active_branch.name,
                'total_files': total_files,
                'local_path': str(local_path),
                'languages': languages,
            }
            
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
        
        Args:
            repo_id: Repository UUID
            
        Returns:
            Repository data or None
        """
        # TODO: Implement database lookup
        local_path = self._get_repo_path(repo_id)
        
        if not local_path.exists():
            return None
        
        return {
            'id': repo_id,
            'name': 'Repository',  # TODO: Get from DB
            'url': '',
            'status': 'ready',
            'local_path': str(local_path),
        }
    
    async def delete_repository(self, repo_id: UUID) -> bool:
        """Delete repository.
        
        Args:
            repo_id: Repository UUID
            
        Returns:
            True if deleted
        """
        local_path = self._get_repo_path(repo_id)
        
        if local_path.exists():
            shutil.rmtree(local_path)
            logger.info(f"Deleted repository {repo_id}")
            return True
        
        return False
    
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
