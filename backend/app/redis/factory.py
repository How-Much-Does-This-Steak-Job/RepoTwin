"""Storage factory for RepoTwin backend."""

import logging
from typing import Union

from app.redis.client import redis_client
from app.redis.store import RedisStore, MemoryStore

logger = logging.getLogger(__name__)

# Global store instances
_redis_store: RedisStore = RedisStore()
_memory_store: MemoryStore = MemoryStore()
_use_memory_store: bool = False


async def get_store() -> Union[RedisStore, MemoryStore]:
    """Get appropriate store instance.
    
    Tries to connect to Redis first. If Redis is unavailable,
    falls back to MemoryStore with a warning logged.
    
    Returns:
        RedisStore if Redis is available, MemoryStore otherwise
        
    Example:
        >>> store = await get_store()
        >>> await store.set_analysis_status("analysis_123", "processing")
    """
    global _use_memory_store
    
    # If already determined to use memory store, return it
    if _use_memory_store:
        return _memory_store
    
    # Try to connect to Redis
    try:
        is_connected = await redis_client.ping()
        if is_connected:
            logger.debug("Using RedisStore for storage")
            return _redis_store
        else:
            logger.warning("Redis not available, falling back to MemoryStore")
            _use_memory_store = True
            return _memory_store
    except Exception as e:
        logger.warning(f"Redis connection failed ({e}), using MemoryStore as fallback")
        _use_memory_store = True
        return _memory_store


async def reset_store_choice() -> None:
    """Reset store choice, forcing a re-check on next get_store() call.
    
    Useful for testing or when Redis becomes available again.
    """
    global _use_memory_store
    _use_memory_store = False
    logger.info("Store choice reset, will re-check Redis availability")


def get_store_sync() -> Union[RedisStore, MemoryStore]:
    """Get memory store synchronously (for initialization/bootstrapping).
    
    Returns:
        MemoryStore instance (safe for synchronous contexts)
        
    Note:
        This should only be used in synchronous contexts where async
        is not available. Prefer get_store() in async contexts.
    """
    return _memory_store
