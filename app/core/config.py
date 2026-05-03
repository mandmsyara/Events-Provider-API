from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_username: str
    postgres_password: str
    postgres_host: str
    postgres_port: str = "5432"
    postgres_database_name: str

    x_api_key: str
    external_api_url: str = (
        "http://student-system-events-provider-web.student-system-events-provider.svc:8000"
    )

    capashino_api_url: str = (
        "http://student-system-capashino-web.student-system-capashino.svc:8000"
    )
    capashino_api_key: str

    outbox_worker_interval: int = 5
    outbox_batch_size: int = 10

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database_name}"

    sentry_dsn: str | None = None
    environment: str = "production"


settings = Settings()
