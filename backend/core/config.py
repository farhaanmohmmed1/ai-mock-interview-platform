import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "True") == "True"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./interview_platform.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
    ]
    
    # AI Models
    HUGGINGFACE_TOKEN: str = os.getenv("HUGGINGFACE_TOKEN", "")
    USE_GPU: bool = os.getenv("USE_GPU", "False") == "True"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt"]
    
    @field_validator("ALLOWED_EXTENSIONS", mode="before")
    @classmethod
    def parse_allowed_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    # Speech Processing
    AUDIO_SAMPLE_RATE: int = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
    MAX_AUDIO_DURATION: int = int(os.getenv("MAX_AUDIO_DURATION", "300"))  # 5 minutes
    
    # Emotion Analysis
    ENABLE_EMOTION_ANALYSIS: bool = os.getenv("ENABLE_EMOTION_ANALYSIS", "True") == "True"
    EMOTION_DETECTION_INTERVAL: int = int(os.getenv("EMOTION_DETECTION_INTERVAL", "2"))
    
    # Interview Configuration
    GENERAL_QUESTIONS_COUNT: int = int(os.getenv("GENERAL_QUESTIONS_COUNT", "5"))
    TECHNICAL_QUESTIONS_COUNT: int = int(os.getenv("TECHNICAL_QUESTIONS_COUNT", "8"))
    HR_QUESTIONS_COUNT: int = int(os.getenv("HR_QUESTIONS_COUNT", "5"))
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
