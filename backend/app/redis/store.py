"""Redis and in-memory store implementations for RepoTwin."""

import json
import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.redis.client import redis_client

logger = logging.getLogger(__name__)


class RedisStore:
    """Redis-based store for analysis data."""
    
    def __init__(self):
        """Initialize store."""
        self._redis = None
    
    async def _get_redis(self):
        """Get Redis connection."""
        if self._redis is None:
            self._redis = await redis_client.connect()
        return self._redis
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        try:
            redis = await self._get_redis()
            return await redis.get(key)
        except Exception as e:
            logger.error(f"Redis get failed for key {key}: {e}")
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set value with optional TTL in seconds."""
        try:
            redis = await self._get_redis()
            if ttl:
                await redis.setex(key, ttl, value)
            else:
                await redis.set(key, value)
            return True
        except Exception as e:
            logger.error(f"Redis set failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete key."""
        try:
            redis = await self._get_redis()
            await redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete failed for key {key}: {e}")
            return False
    
    async def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern."""
        try:
            redis = await self._get_redis()
            return [key async for key in redis.scan_iter(match=pattern)]
        except Exception as e:
            logger.error(f"Redis keys failed for pattern {pattern}: {e}")
            return []
    
    async def hget(self, key: str, field: str) -> Optional[str]:
        """Get hash field value."""
        try:
            redis = await self._get_redis()
            return await redis.hget(key, field)
        except Exception as e:
            logger.error(f"Redis hget failed for key {key}, field {field}: {e}")
            return None
    
    async def hset(self, key: str, field: str, value: str) -> bool:
        """Set hash field value."""
        try:
            redis = await self._get_redis()
            await redis.hset(key, field, value)
            return True
        except Exception as e:
            logger.error(f"Redis hset failed for key {key}, field {field}: {e}")
            return False
    
    async def hgetall(self, key: str) -> Dict[str, str]:
        """Get all hash fields."""
        try:
            redis = await self._get_redis()
            return await redis.hgetall(key)
        except Exception as e:
            logger.error(f"Redis hgetall failed for key {key}: {e}")
            return {}
    
    async def hdel(self, key: str, field: str) -> bool:
        """Delete hash field."""
        try:
            redis = await self._get_redis()
            await redis.hdel(key, field)
            return True
        except Exception as e:
            logger.error(f"Redis hdel failed for key {key}, field {field}: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        try:
            redis = await self._get_redis()
            return await redis.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis exists failed for key {key}: {e}")
            return False


class MemoryStore:
    """In-memory store fallback for local development."""
    
    def __init__(self):
        """Initialize in-memory storage."""
        self._data: Dict[str, Any] = {}
        self._ttl: Dict[str, float] = {}
        self._hashes: Dict[str, Dict[str, str]] = {}
        logger.info("Using in-memory store (Redis unavailable)")
    
    def _is_expired(self, key: str) -> bool:
        """Check if key is expired."""
        if key in self._ttl:
            import time
            if time.time() > self._ttl[key]:
                self._data.pop(key, None)
                self._ttl.pop(key, None)
                return True
        return False
    
    async def get(self, key: str) -> Optional[str]:
        """Get value by key."""
        if self._is_expired(key):
            return None
        return self._data.get(key)
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> bool:
        """Set value with optional TTL."""
        self._data[key] = value
        if ttl:
            import time
            self._ttl[key] = time.time() + ttl
        return True
    
    async def delete(self, key: str) -> bool:
        """Delete key."""
        self._data.pop(key, None)
        self._ttl.pop(key, None)
        self._hashes.pop(key, None)
        return True
    
    async def keys(self, pattern: str) -> List[str]:
        """Get keys matching pattern (simple substring match)."""
        import fnmatch
        return [k for k in self._data.keys() if fnmatch.fnmatch(k, pattern)]
    
    async def hget(self, key: str, field: str) -> Optional[str]:
        """Get hash field value."""
        if self._is_expired(key):
            return None
        return self._hashes.get(key, {}).get(field)
    
    async def hset(self, key: str, field: str, value: str) -> bool:
        """Set hash field value."""
        if key not in self._hashes:
            self._hashes[key] = {}
        self._hashes[key][field] = value
        return True
    
    async def hgetall(self, key: str) -> Dict[str, str]:
        """Get all hash fields."""
        if self._is_expired(key):
            return {}
        return self._hashes.get(key, {}).copy()
    
    async def hdel(self, key: str, field: str) -> bool:
        """Delete hash field."""
        if key in self._hashes:
            self._hashes[key].pop(field, None)
        return True
    
    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        if self._is_expired(key):
            return False
        return key in self._data or key in self._hashes
