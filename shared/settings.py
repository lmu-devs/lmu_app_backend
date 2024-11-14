from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    
    API_KEY: str
    
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str

    
    CORS_ORIGINS: list[str] = [
        "https://lmu-students.lmu-dev.org",
        "http://localhost:53480"
    ]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()