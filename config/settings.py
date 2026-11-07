import os
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
EXPORTS_DIR = BASE_DIR / "exports"

DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseSettings):
    APP_NAME: str = "PharmaLit AI"
    APP_VERSION: str = "1.0.0"
    DATABASE_PATH: Path = DATA_DIR / "pharmalit.db"
    
    # Gemini AI Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    DEFAULT_ANALYSIS_MODE: str = os.getenv("DEFAULT_ANALYSIS_MODE", "auto")
    MAX_BATCH_SIZE: int = 20
    
    # Search API Defaults
    PUBMED_EMAIL: str = os.getenv("PUBMED_EMAIL", "pharmalit.research@example.com")
    PUBMED_API_KEY: str = os.getenv("PUBMED_API_KEY", "")
    REQUEST_TIMEOUT: int = 25
    USER_AGENT: str = "PharmaLitAI/1.0 (Biomedical Research Platform; mailto:pharmalit.research@example.com)"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
