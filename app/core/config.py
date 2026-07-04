from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Trinity AI Backend"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # API Keys
    GEMINI_API_KEY: str = ""
    ELEVENLABS_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Databases
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    POSTGRES_URL: str = "postgresql://trinity:password@localhost:5432/trinity_analytics"
    REDIS_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
