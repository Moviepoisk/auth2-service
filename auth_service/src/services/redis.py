from fastapi import Depends
from redis import Redis
from src.core.config.base import base_auth_jwt_settings
from src.core.dependencies import get_redis


class RedisService:
    def __init__(self, redis: Redis) -> None:
        self.redis = redis

    async def _delete_token_by_email(self, email: str, token: str) -> None:
        async for key in self.redis.scan_iter(f"{email}:{token}:*"):
            await self.redis.delete(key)

    async def delete_tokens(self, email: str) -> None:
        async with self.redis.pipeline() as p:
            await self._delete_token_by_email(email, "access_token")
            await self._delete_token_by_email(email, "refresh_token")
            await p.execute()

    async def set_tokens(self, email: str, access_token: str, refresh_token: str) -> None:
        async with self.redis.pipeline() as p:
            await self.delete_tokens(email=email)
            await p.setex(
                f"{email}:access_token:{access_token}",
                base_auth_jwt_settings.access_expires_time,
                access_token,
            )
            await p.setex(
                f"{email}:refresh_token:{refresh_token}",
                base_auth_jwt_settings.refresh_expires_time,
                refresh_token,
            )
            await p.execute()

    async def check_token_exists(self, email: str, token_name: str, token_value: str) -> bool:
        return bool(await self.redis.get(f"{email}:{token_name}:{token_value}"))

    async def set_refresh_token(self, email: str, refresh_token: str) -> None:
        async with self.redis.pipeline() as p:
            await self.delete_tokens(email=email)
            await p.setex(
                f"{email}:refresh_token:{refresh_token}",
                base_auth_jwt_settings.refresh_expires_time,
                refresh_token,
            )
            await p.execute()

    async def revoke_token(self, email: str, token_name: str, token_value: str, ttl: int) -> None:
        await self.redis.setex(f"{email}:revoke:{token_name}:{token_value}", ttl, "true")


def get_redis_service(redis: Redis = Depends(get_redis)) -> RedisService:
    return RedisService(redis=redis)
