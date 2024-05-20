from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class TestSettings(BaseSettings):
    postgres_user: str = Field("test", alias="POSTGRES_USER")
    postgres_password: str = Field("test", alias="POSTGRES_PASSWORD")
    postgres_db: str = Field("test", alias="POSTGRES_DB")
    postgres_host: str = Field("test_db", alias="POSTGRES_HOST")
    postgres_port: int = Field(5432, alias="POSTGRES_PORT")

    redis_host: str = Field("127.0.0.1:6379", alias="REDIS_HOST")
    redis_port: int = Field(6379, alias="REDIS_PORT")
    service_url: str = Field("http://127.0.0.1:8000", alias="SERVICE_URL")

    model_config = SettingsConfigDict(extra="ignore", env_file="tests.env")

    def get_postgres_dsn(self):
        return {
            "dbname": self.postgres_db,
            "user": self.postgres_user,
            "password": self.postgres_password,
            "host": self.postgres_host,
            "port": self.postgres_port,
        }


test_settings = TestSettings()
