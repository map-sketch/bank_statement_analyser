import os
from pydantic_settings import BaseSettings

# Calculate the root directory of the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
DEFAULT_DB_URL = f"sqlite:///{os.path.join(DATA_DIR, 'bank_statement.db')}"

class Settings(BaseSettings):
    DATABASE_URL: str = DEFAULT_DB_URL
    UPLOAD_DIR: str = os.path.join(DATA_DIR, "uploads")
    ML_MODEL_PATH: str = os.path.join(BASE_DIR, "ml_models", "category_classifier.pkl")
    ML_VECTORIZER_PATH: str = os.path.join(BASE_DIR, "ml_models", "tfidf_vectorizer.pkl")
    SESSION_EXPIRY_HOURS: int = 24
    MAX_UPLOAD_SIZE_MB: int = 50
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"

settings = Settings()

# Force SQLite if a legacy Postgres URL is lingering in environment variables
if settings.DATABASE_URL.startswith("postgres"):
    settings.DATABASE_URL = DEFAULT_DB_URL
