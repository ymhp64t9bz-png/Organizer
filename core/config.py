"""
ORBIT - Core Configuration
Configurações centrais do backend
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configurações da aplicação"""
    
    # App
    APP_NAME: str = "ORBIT"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://orbit:orbit@localhost:5432/orbit"
    )
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Redis (opcional, para cache)
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    
    # AI Providers
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3:8b")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    
    # Whisper
    WHISPER_MODEL: str = os.getenv("WHISPER_MODEL", "base")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "orbit-super-secret-key-change-in-production")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://orbit.app"
    ]
    
    # Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/webp"]
    ALLOWED_AUDIO_TYPES: list = ["audio/webm", "audio/mp3", "audio/wav", "audio/m4a"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Retorna singleton das configurações"""
    return Settings()


settings = get_settings()
