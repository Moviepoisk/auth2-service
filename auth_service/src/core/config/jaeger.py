from pydantic_settings import BaseSettings, SettingsConfigDict


class JaegerSettings(BaseSettings):
    """Jaeger Creadentials class."""

    model_config = SettingsConfigDict(
        extra="ignore",
        env_prefix="jaeger_",
        env_file_encoding="utf-8",
    )
    agent_host_name: str
    agent_port: int
    enable: bool = False


jaeger_settings = JaegerSettings()
