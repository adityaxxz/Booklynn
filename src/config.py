from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from pydantic import SecretStr
from dotenv import load_dotenv
from pathlib import Path

# load the .env file located in the same directory as this file (src/.env)
DOTENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(DOTENV_PATH)

class Settings(BaseSettings):
    # Use DATABASE_URL from environment only (PostgreSQL)
    DATABASE_URL: str = os.getenv("DATABASE_URL") or ""
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") or ""
    JWT_ALGORITHM: str = "HS256"
    
    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Mail configuration
    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME") or ""
    MAIL_PASSWORD: SecretStr = SecretStr(os.getenv("MAIL_PASSWORD") or "")
    MAIL_FROM: str = os.getenv("MAIL_FROM") or ""
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_FROM_NAME: str = "Admin@Booklynn"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True
    DOMAIN: str = "localhost:8000"

    model_config = SettingsConfigDict(
        env_file=DOTENV_PATH,
        extra="ignore"
    )



# Create settings instance
Config = Settings()