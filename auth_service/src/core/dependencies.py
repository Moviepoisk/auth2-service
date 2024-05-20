from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine

async_pg_engine: AsyncEngine | None = None

redis: Redis | None = None


async def get_pg_connection() -> AsyncEngine | None:
    """Return AsyncEngine engine instance."""
    return async_pg_engine


async def get_redis() -> Redis | None:
    """Return async Redis instance."""
    return redis
