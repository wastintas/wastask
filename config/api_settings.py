"""
API-specific settings
"""
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings

class APISettings(BaseSettings):
    """API settings with defaults"""
    
    # Security
    secret_key: str = Field(default="dev-secret-key-change-in-production")
    cors_origins: List[str] = Field(default=["*"])
    
    # Debug
    debug: bool = Field(default=True)
    
    class Config:
        env_prefix = "WASTASK_"

# Global settings instance
api_settings = APISettings()