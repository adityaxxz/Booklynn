from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    # Default to async SQLite for local development
    DATABASE_URL: str = "sqlite+aiosqlite:///./books.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

# Create settings instance
config = Settings()