"""
Configuración centralizada para la aplicación Flask
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuración de la aplicación"""
    
    # Entorno
    ENV: str = os.getenv("FLASK_ENV", "development")
    DEBUG: bool = ENV == "development"
    
    # Flask
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES: int = 3600  # 1 hora
    JWT_REFRESH_TOKEN_EXPIRES: int = 604800  # 7 días
    JWT_COOKIE_SECURE: bool = ENV != "development"
    JWT_COOKIE_HTTPONLY: bool = True
    JWT_COOKIE_SAMESITE: str = "Lax"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///spm_v2.db")
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/spm_backend.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
