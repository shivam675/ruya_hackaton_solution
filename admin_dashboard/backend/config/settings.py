"""
Application Configuration Settings
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "hr_recruitment_db"
    
    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # SMTP
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str
    smtp_password: str
    smtp_from: str
    
    # Microservices
    cv_agent_url: str = "http://localhost:8002"
    email_agent_url: str = "http://localhost:8003"
    interview_agent_url: str = "http://localhost:8004"
    hr_chat_agent_url: str = "http://localhost:8005"
    
    # Storage
    cv_storage_path: str = "../storage/cvs"
    recording_storage_path: str = "../storage/recordings"
    transcript_storage_path: str = "../storage/transcripts"
    
    # CORS - Allow all origins for LAN access (use specific IPs in production)
    allowed_origins: str = "*"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    def ensure_storage_directories(self):
        """Create storage directories if they don't exist"""
        base_path = Path(__file__).parent.parent.parent
        
        paths = [
            base_path / self.cv_storage_path,
            base_path / self.recording_storage_path,
            base_path / self.transcript_storage_path,
        ]
        
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
settings.ensure_storage_directories()
