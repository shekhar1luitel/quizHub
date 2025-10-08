from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
import os

class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://quiz:quiz@localhost:5432/quizhub"
    jwt_secret: str = "dev-secret"
    jwt_alg: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14

    backend_cors_origins: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @property
    def cors_origins(self) -> List[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

settings = Settings()
