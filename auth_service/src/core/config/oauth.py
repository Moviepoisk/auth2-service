from pydantic import Field
from pydantic_settings import BaseSettings


class OAuthProviderCredentials(BaseSettings):
    """Base class for OAuth provider credentials."""

    auth_url: str
    token_url: str
    user_info_url: str
    client_id: str
    client_secret: str
    client_redirect_uri: str


class OAuthYandexCredentials(OAuthProviderCredentials):
    """OAuth Yandex Credentials class."""

    class Config:
        env_prefix = "oauth_yandex_"


class Settings(BaseSettings):
    """Settings class for loading OAuth provider configurations from environment variables."""

    yandex: OAuthYandexCredentials = Field(default_factory=OAuthYandexCredentials)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


oauth_settings = Settings()
