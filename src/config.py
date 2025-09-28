from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Default to async SQLite for local development
    DATABASE_URL: str = "sqlite+aiosqlite:///./books.db"
    JWT_SECRET_KEY: str = "e698218fbf1d9d46b06a6c1aa41b3124"
    JWT_ALGORITHM: str = "HS256"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

# Create settings instance
Config = Settings()