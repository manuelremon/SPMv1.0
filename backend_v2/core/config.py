"""
Backend v2.0 - Configuración de entornos
Soporta Dev, Test y Producción con lectura desde .env
"""
from __future__ import annotations

import os
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración base compartida por todos los entornos"""
    
    # Entorno
    ENV: Literal["development", "test", "production"] = "development"
    DEBUG: bool = False
    
    # Seguridad
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_TTL: int = 3600  # 1 hora
    JWT_COOKIE_NAME: str = "spm_token"
    JWT_COOKIE_HTTPONLY: bool = True
    JWT_COOKIE_SECURE: bool = False  # True en producción
    JWT_COOKIE_SAMESITE: Literal["Lax", "Strict", "None"] = "Lax"
    
    # Base de datos
    DATABASE_URL: str = "sqlite:///./spm_v2.db"
    
    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    
    # Rate limiting
    RATE_LIMIT_ENABLED: bool = False
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


class DevelopmentSettings(Settings):
    """Configuración para desarrollo local"""
    ENV: Literal["development"] = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"
    JWT_COOKIE_SECURE: bool = False


class TestSettings(Settings):
    """Configuración para tests"""
    ENV: Literal["test"] = "test"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///:memory:"  # In-memory para tests
    JWT_ACCESS_TOKEN_TTL: int = 60  # 1 minuto para tests
    RATE_LIMIT_ENABLED: bool = False


class ProductionSettings(Settings):
    """Configuración para producción"""
    ENV: Literal["production"] = "production"
    DEBUG: bool = False
    JWT_COOKIE_SECURE: bool = True  # HTTPS only
    JWT_COOKIE_SAMESITE: Literal["Strict"] = "Strict"
    RATE_LIMIT_ENABLED: bool = True
    LOG_LEVEL: str = "WARNING"


def get_settings() -> Settings:
    """
    Factory para obtener configuración según entorno.
    Lee la variable ENV del sistema o .env
    """
    env = os.getenv("ENV", "development").lower()
    
    settings_map = {
        "development": DevelopmentSettings,
        "test": TestSettings,
        "production": ProductionSettings,
    }
    
    settings_class = settings_map.get(env, DevelopmentSettings)
    return settings_class()


# Singleton global
settings = get_settings()
