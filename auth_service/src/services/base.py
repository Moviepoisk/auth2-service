from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker


class BaseService:
    def __init__(self, pg_connection: AsyncEngine, redis: Redis):
        self.pg_connection = pg_connection
        self.redis = redis

    def get_session(self) -> AsyncSession:
        """Get Async SqlAlchemy connection."""
        return sessionmaker(self.pg_connection, expire_on_commit=False, class_=AsyncSession)()
