from async_fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthServiceSettings(BaseSettings):
    """Auth service settings for FastAPI project."""

    model_config = SettingsConfigDict(
        extra="ignore",
        env_prefix="auth_service_",
        env_file_encoding="utf-8",
        env_file=".env",
    )
    name: str
    host: str
    port: int
    docs_url: str
    openapi_url: str
    workers: int
    log_level: str

    db_host: str
    db_port: int
    db_user: str
    db_password: str
    db_name: str

    def get_dsn(self):
        """Get dsn to connect to postgres"""
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


class RedisSettings(BaseSettings):
    """Redis settings class."""

    model_config = SettingsConfigDict(
        extra="ignore",
        env_prefix="redis_",
        env_file_encoding="utf-8",
        env_file=".env",
    )
    host: str
    port: int


class BaseAuthJWTSettings(BaseSettings):
    """BaseAuthJWT settings class."""

    model_config = SettingsConfigDict(
        extra="ignore",
        env_prefix="authjwt_",
        env_file_encoding="utf-8",
        env_file=".env",
    )
    access_expires_time: int
    refresh_expires_time: int
    secret_key: str
    token_location: str
    cookie_csrf_protect: bool


auth_service_settings = AuthServiceSettings()
redis_settings = RedisSettings()
base_auth_jwt_settings = BaseAuthJWTSettings()


# TODO в доке конфиг прописывается так, подумать как привести в примеру выше
class AuthJWTSettings(BaseModel):
    """https://sijokun.github.io/async-fastapi-jwt-auth/usage/jwt-in-cookies/"""

    authjwt_secret_key: str = base_auth_jwt_settings.secret_key
    authjwt_token_location: set = {base_auth_jwt_settings.token_location}
    authjwt_cookie_csrf_protect: bool = base_auth_jwt_settings.cookie_csrf_protect
    authjwt_denylist_enabled: bool = True
    authjwt_denylist_token_checks: set = {"access", "refresh"}


@AuthJWT.load_config
def get_config():
    return AuthJWTSettings()
