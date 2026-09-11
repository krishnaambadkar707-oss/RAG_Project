import os
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseModel as BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

IS_VERCEL = os.getenv("VERCEL") == "1" or os.getenv("VERCEL_ENV") is not None

def get_default_db_url():
    if IS_VERCEL:
        return "sqlite:////tmp/rag_assistant.db"
    return f"sqlite:///{os.path.join(BASE_DIR, 'rag_assistant.db')}"

def get_default_chroma_dir():
    if IS_VERCEL:
        return "/tmp/chroma_data"
    return os.path.join(BASE_DIR, "chroma_data")

def get_default_upload_dir():
    if IS_VERCEL:
        return "/tmp/uploads"
    return os.path.join(BASE_DIR, "uploads")

class Settings(BaseSettings):
    PROJECT_NAME: str = "Enterprise RAG Knowledge Assistant"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENV: str = "development"
    
    # Database (Absolute path to project root rag_assistant.db)
    DATABASE_URL: str = os.getenv("DATABASE_URL", get_default_db_url())
    
    # Authentication
    JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecret_jwt_key_change_me_in_production_12345")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours
    
    # RAG Settings
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "sentence-transformers") # sentence-transformers | openai | gemini
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "mock") # mock | openai | gemini
    
    # API Keys
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Vector store & document paths (Absolute paths to project root)
    CHROMA_DB_DIR: str = os.getenv("CHROMA_DB_DIR", get_default_chroma_dir())
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", get_default_upload_dir())
    BENCHMARK_FILE: str = os.getenv("BENCHMARK_FILE", os.path.join(BASE_DIR, "data", "benchmark_test_set.json"))

    # Chunking Defaults
    DEFAULT_CHUNK_SIZE: int = 600
    DEFAULT_CHUNK_OVERLAP: int = 100
    TOP_K_RETRIEVAL: int = 5

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()

try:
    os.makedirs(settings.CHROMA_DB_DIR, exist_ok=True)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
except OSError as e:
    print(f"[Config Warning] Directory creation warning: {e}")


