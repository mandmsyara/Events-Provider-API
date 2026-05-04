from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_username: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: str = "5432"
    postgres_database_name: str = "events_db"

    x_api_key: str = "test-api-key"
    external_api_url: str = (
        "http://student-system-events-provider-web.student-system-events-provider.svc:8000"
    )

    capashino_api_url: str = (
        "http://student-system-capashino-web.student-system-capashino.svc:8000"
    )
    capashino_api_key: str = "test-capashino-key"

    outbox_worker_interval: int = 5
    outbox_batch_size: int = 10

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_username}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_database_name}"

    sentry_dsn: str | None = None
    environment: str = "production"


settings = Settings()
