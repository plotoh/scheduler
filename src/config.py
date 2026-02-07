# src/config.py
from pydantic_settings import BaseSettings
from authx import AuthXConfig
from typing import List, Optional


class Settings(BaseSettings):
    """Настройки приложения"""

    # Основные настройки
    APP_NAME: str = "FastAPI Books API"
    APP_DESCRIPTION: str = "FastAPI приложение с аутентификацией и управлением книгами"
    APP_VERSION: str = "1.0.0"

    # Сервер
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://127.0.0.1:8000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Документация
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"

    # Логирование
    LOG_LEVEL: str = "info"

    # PostgreSQL
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/scheduler_db"
    DB_POOL_MIN_SIZE: int = 1
    DB_POOL_MAX_SIZE: int = 10

    # JWT (AuthX)
    JWT_SECRET_KEY: str = "my_very_secret_key_that_is_long_enough_for_hs256_algorithm_1234567890"
    JWT_ACCESS_TOKEN_EXPIRES: int = 86400
    JWT_REFRESH_TOKEN_EXPIRES: int = 2592000

    class Config:
        env_file = ".env"
        case_sensitive = True


def get_authx_config() -> AuthXConfig:
    """Конфигурация для AuthX"""
    config = AuthXConfig()
    config.JWT_SECRET_KEY = settings.JWT_SECRET_KEY
    config.JWT_ACCESS_COOKIE_NAME = 'access_token'
    config.JWT_REFRESH_COOKIE_NAME = 'refresh_token'
    config.JWT_TOKEN_LOCATION = ['cookies', 'headers']
    config.JWT_ACCESS_TOKEN_EXPIRES = settings.JWT_ACCESS_TOKEN_EXPIRES
    config.JWT_REFRESH_TOKEN_EXPIRES = settings.JWT_REFRESH_TOKEN_EXPIRES
    config.JWT_ALGORITHM = 'HS256'
    config.JWT_COOKIE_CSRF_PROTECT = False
    config.JWT_COOKIE_SAMESITE = 'lax'
    return config


# Глобальный экземпляр настроек
settings = Settings()

