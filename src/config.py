from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from pathlib import Path
from dotenv import load_dotenv
import os

# load the .env file located in the same directory as this file (src/.env)
DOTENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(DOTENV_PATH)


class Settings(BaseSettings):
    # Use DATABASE_URL from env (PostgreSQL), always .get_secret_value() to get the secret value
    DATABASE_URL: SecretStr = SecretStr(os.getenv("DATABASE_URL") or "")
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY") or ""
    JWT_ALGORITHM: str = "HS256"
    
    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_URL: str = "redis://localhost:6379/0"

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

#Celery config
broker_url = Config.REDIS_URL
result_backend = Config.REDIS_URL
broker_connection_retry_on_startup = True
worker_pool = "solo" if os.name == "nt" else None