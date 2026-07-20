from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./data/bank_statement.db"
    UPLOAD_DIR: str = "./data/uploads"
    ML_MODEL_PATH: str = "./ml_models/category_classifier.pkl"
    ML_VECTORIZER_PATH: str = "./ml_models/tfidf_vectorizer.pkl"
    SESSION_EXPIRY_HOURS: int = 24
    MAX_UPLOAD_SIZE_MB: int = 50
    CORS_ORIGINS: str = "*"

    class Config:
        env_file = ".env"

settings = Settings()
