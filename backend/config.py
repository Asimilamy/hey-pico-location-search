"""
Configuration management for the LLM Maps application
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from .env file"""
    
    # Google Maps API
    google_maps_api_key: str
    
    # OpenWebUI Configuration
    openweb_ui_url: str = "http://localhost:8000"
    openweb_ui_api_key: str = ""
    openweb_ui_model: str = "mistral"
    
    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8001
    
    # Rate Limiting
    rate_limit_per_minute: int = 30
    
    # Environment
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


settings = get_settings()
