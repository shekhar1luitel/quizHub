from collections.abc import Sequence
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg://quiz:quiz@localhost:5432/quizhub",
        description="SQLAlchemy compatible database URL",
    )
    database_pool_size: int = Field(default=15, ge=5, le=50)
    database_max_overflow: int = Field(default=10, ge=0, le=50)
    redis_url: str | None = Field(default=None, description="Optional Redis connection URL")

    jwt_secret: str = Field(default="dev-secret")
    jwt_refresh_secret: str | None = None
    jwt_alg: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30, ge=5, le=120)
    refresh_token_expire_minutes: int = Field(default=60 * 24 * 14, ge=60)

    backend_cors_origins: str = "http://localhost:5173"

    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None
    smtp_tls_ssl: bool = True
    mail_from_name: str | None = None
    mail_from_email: str | None = None

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

    @property
    def effective_jwt_refresh_secret(self) -> str:
        return self.jwt_refresh_secret or self.jwt_secret

    @property
    def mail_settings(self) -> dict[str, str | int | bool | None]:
        return {
            "host": self.smtp_host,
            "port": self.smtp_port,
            "username": self.smtp_username,
            "password": self.smtp_password,
            "tls_ssl": self.smtp_tls_ssl,
            "from_name": self.mail_from_name,
            "from_email": self.mail_from_email,
        }


settings = Settings()
