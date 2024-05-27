from contextlib import asynccontextmanager
from typing import Any

from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, ORJSONResponse
from fastapi_pagination import add_pagination
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine

from src.services.rate_limit import RateLimitMiddleware
from src.api.v1.middlewares import before_request
from src.api.v1.jaeger import configure_tracer
from src.api import router as auth_router
from src.core import dependencies
from src.core.config import auth_service_settings, redis_settings


@asynccontextmanager
async def lifespan(_: FastAPI) -> Any:
    """Open connections with dependent services.

    :param FastAPI _: FastAPI app instance.
    """

    dependencies.async_pg_engine = create_async_engine(auth_service_settings.get_dsn())
    dependencies.redis = Redis(**redis_settings.model_dump())
    yield
    await dependencies.async_pg_engine.dispose()
    await dependencies.redis.close()


# Jaeger
configure_tracer(service_name=auth_service_settings.name)

app = FastAPI(
    title=auth_service_settings.name,
    docs_url=auth_service_settings.docs_url,
    openapi_url=auth_service_settings.openapi_url,
    default_response_class=ORJSONResponse,
    lifespan=lifespan,
)
add_pagination(app)


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(_: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.include_router(auth_router)

# Jaeger
app.middleware("http")(before_request)
FastAPIInstrumentor.instrument_app(app)

# Добавляем middleware для rate limiting
app.add_middleware(RateLimitMiddleware)
