import datetime
import redis
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from src.core.config import redis_settings


# Установим лимит на 10 запросов в минуту
REQUEST_LIMIT_PER_MINUTE = 10

# Создайте подключение к Redis
redis_conn = redis.Redis(host=redis_settings.host, port=redis_settings.port, db=0)


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        authorize = request.scope.get("authorize")

        if not authorize:
            return await call_next(request)

        await authorize.jwt_required()

        current_user = await authorize.get_jwt_subject()
        if not current_user:
            raise HTTPException(status_code=401, detail="Unauthorized")

        # Логика ограничения скорости
        now = datetime.datetime.now()
        key = f"{current_user}:{now.minute}"

        pipe = redis_conn.pipeline()
        pipe.incr(key, 1)
        pipe.expire(key, 59)
        result = await pipe.execute()
        request_number = result[0]

        if request_number > REQUEST_LIMIT_PER_MINUTE:
            raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too Many Requests")

        response = await call_next(request)
        return response
