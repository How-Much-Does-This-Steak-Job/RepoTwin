"""In-memory storage layer for analysis jobs."""

import json
import logging
from typing import Any, Dict, List, Optional

import asyncio

logger = logging.getLogger(__name__)


class MemoryStore:
    """In-memory storage for analysis jobs using dict + asyncio.Lock.
    
    Provides the same interface as RedisStore for seamless fallback.
    """
    
    def __init__(self):
        """Initialize in-memory store."""
        # Storage dictionaries
        self._status: Dict[str, str] = {}
        self._progress: Dict[str, int] = {}
        self._result: Dict[str, str] = {}  # JSON serialized
        self._metadata: Dict[str, str] = {}  # JSON serialized
        self._error: Dict[str, str] = {}
        self._active_set: set = set()
        
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()
        
        logger.info("MemoryStore initialized")
    
    # Status operations
    async def set_analysis_status(self, analysis_id: str, status: str, ttl: Optional[int] = None) -> None:
        """Set analysis status.
        
        Args:
            analysis_id: Analysis ID
            status: Status value (e.g., "pending", "processing", "completed", "failed")
            ttl: TTL in seconds (optional, ignored in memory store)
        """
        async with self._lock:
            self._status[analysis_id] = status
            logger.debug(f"[MemoryStore] Set status for {analysis_id}: {status}")
    
    async def get_analysis_status(self, analysis_id: str) -> Optional[str]:
        """Get analysis status.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Status value or None if not found
        """
        async with self._lock:
            return self._status.get(analysis_id)
    
    # Progress operations
    async def set_analysis_progress(self, analysis_id: str, progress: int, ttl: Optional[int] = None) -> None:
        """Set analysis progress.
        
        Args:
            analysis_id: Analysis ID
            progress: Progress percentage (0-100)
            ttl: TTL in seconds (optional, ignored in memory store)
        """
        async with self._lock:
            self._progress[analysis_id] = progress
            logger.debug(f"[MemoryStore] Set progress for {analysis_id}: {progress}%")
    
    async def get_analysis_progress(self, analysis_id: str) -> Optional[int]:
        """Get analysis progress.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Progress percentage or None if not found
        """
        async with self._lock:
            return self._progress.get(analysis_id)
    
    # Result operations
    async def set_analysis_result(self, analysis_id: str, result: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Set analysis result.
        
        Args:
            analysis_id: Analysis ID
            result: Analysis result data
            ttl: TTL in seconds (optional, ignored in memory store)
        """
        async with self._lock:
            self._result[analysis_id] = json.dumps(result)
            logger.debug(f"[MemoryStore] Set result for {analysis_id}")
    
    async def get_analysis_result(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis result.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Analysis result data or None if not found
        """
        async with self._lock:
            result = self._result.get(analysis_id)
            return json.loads(result) if result else None
    
    # Metadata operations
    async def set_analysis_metadata(self, analysis_id: str, metadata: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Set analysis metadata.
        
        Args:
            analysis_id: Analysis ID
            metadata: Analysis metadata
            ttl: TTL in seconds (optional, ignored in memory store)
        """
        async with self._lock:
            self._metadata[analysis_id] = json.dumps(metadata)
            logger.debug(f"[MemoryStore] Set metadata for {analysis_id}")
    
    async def get_analysis_metadata(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get analysis metadata.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Analysis metadata or None if not found
        """
        async with self._lock:
            metadata = self._metadata.get(analysis_id)
            return json.loads(metadata) if metadata else None
    
    # Error operations
    async def set_analysis_error(self, analysis_id: str, error: str, ttl: Optional[int] = None) -> None:
        """Set analysis error.
        
        Args:
            analysis_id: Analysis ID
            error: Error message
            ttl: TTL in seconds (optional, ignored in memory store)
        """
        async with self._lock:
            self._error[analysis_id] = error
            logger.debug(f"[MemoryStore] Set error for {analysis_id}: {error}")
    
    async def get_analysis_error(self, analysis_id: str) -> Optional[str]:
        """Get analysis error.
        
        Args:
            analysis_id: Analysis ID
            
        Returns:
            Error message or None if not found
        """
        async with self._lock:
            return self._error.get(analysis_id)
    
    # Cleanup operations
    async def delete_analysis(self, analysis_id: str) -> None:
        """Delete all analysis data.
        
        Args:
            analysis_id: Analysis ID
        """
        async with self._lock:
            self._status.pop(analysis_id, None)
            self._progress.pop(analysis_id, None)
            self._result.pop(analysis_id, None)
            self._metadata.pop(analysis_id, None)
            self._error.pop(analysis_id, None)
            self._active_set.discard(analysis_id)
            logger.debug(f"[MemoryStore] Deleted analysis {analysis_id}")
    
    # Active set operations
    async def add_to_active_set(self, analysis_id: str) -> None:
        """Add analysis to active set.
        
        Args:
            analysis_id: Analysis ID
        """
        async with self._lock:
            self._active_set.add(analysis_id)
            logger.debug(f"[MemoryStore] Added {analysis_id} to active set")
    
    async def remove_from_active_set(self, analysis_id: str) -> None:
        """Remove analysis from active set.
        
        Args:
            analysis_id: Analysis ID
        """
        async with self._lock:
            self._active_set.discard(analysis_id)
            logger.debug(f"[MemoryStore] Removed {analysis_id} from active set")
    
    async def get_active_analyses(self) -> List[str]:
        """Get all active analysis IDs.
        
        Returns:
            List of active analysis IDs
        """
        async with self._lock:
            return list(self._active_set)
