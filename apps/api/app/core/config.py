import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Set writable cache directories for Matplotlib, Joblib and SHAP in sandbox
os.environ["MPLCONFIGDIR"] = str(BASE_DIR / "storage" / "cache")
(BASE_DIR / "storage" / "cache").mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    PROJECT_NAME: str = "NutriPredict AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment & Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "nutripredict-super-secret-scientific-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 24 hours
    
    # Database (SQLite for local dev, PostgreSQL for production)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./nutripredict.db")
    
    # Storage
    STORAGE_DIR: Path = BASE_DIR / "storage"
    UPLOAD_DIR: Path = BASE_DIR / "storage" / "uploads"
    ARTIFACTS_DIR: Path = BASE_DIR / "storage" / "artifacts"
    REPORTS_DIR: Path = BASE_DIR / "storage" / "reports"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Scientific Governance
    DEMO_DATA_TAG: str = "DATOS SINTÉTICOS — NO REPRESENTAN LA REALIDAD"
    WHO_ANEMIA_CUTOFF_HB: float = 11.0 # g/dL for 6-59 months
    WHO_STUNTING_CUTOFF_HAZ: float = -2.0 # SD
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure storage directories exist
settings.STORAGE_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
