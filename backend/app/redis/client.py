"""Redis client with connection pooling."""

import logging
from typing import Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client with connection pooling."""
    
    _instance: Optional["RedisClient"] = None
    _redis: Optional[Redis] = None
    
    def __new__(cls):
        """Singleton pattern for Redis client."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(self) -> Redis:
        """Initialize Redis connection pool.
        
        Returns:
            Redis client instance
            
        Raises:
            ConnectionError: If Redis connection fails
        """
        if self._redis is None:
            try:
                logger.info(f"Connecting to Redis at {settings.redis_url}")
                self._redis = aioredis.from_url(
                    str(settings.redis_url),
                    max_connections=settings.redis_pool_size,
                    decode_responses=True,
                )
                # Test connection
                await self._redis.ping()
                logger.info("Redis connection established successfully")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise ConnectionError(f"Redis connection failed: {e}")
        
        return self._redis
    
    async def ping(self) -> bool:
        """Check if Redis connection is alive.
        
        Returns:
            True if connection is alive, False otherwise
        """
        try:
            redis = await self.connect()
            await redis.ping()
            return True
        except Exception as e:
            logger.warning(f"Redis ping failed: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Close Redis connection pool."""
        if self._redis:
            await self._redis.close()
            self._redis = None
            logger.info("Redis connection closed")
    
    @property
    def redis(self) -> Redis:
        """Get Redis client instance.
        
        Returns:
            Redis client
            
        Raises:
            RuntimeError: If Redis is not connected
        """
        if self._redis is None:
            raise RuntimeError("Redis client not initialized. Call connect() first.")
        return self._redis


# Global Redis client instance
redis_client = RedisClient()


async def get_redis_client() -> RedisClient:
    """Get Redis client instance.
    
    Returns:
        RedisClient instance
    """
    return redis_client
