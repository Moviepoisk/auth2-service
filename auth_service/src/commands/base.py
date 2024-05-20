from sqlalchemy.ext.asyncio import create_async_engine
from src.core.config.base import auth_service_settings
from src.services import RoleService
from src.services.role import get_role_service
from src.services.user import UserService, get_user_service

async_engine = create_async_engine(auth_service_settings.get_dsn())

user_service: UserService = get_user_service(pg_connection=async_engine, redis=None)
role_service: RoleService = get_role_service(pg_connection=async_engine, redis=None)
