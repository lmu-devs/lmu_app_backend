from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    
    # Base URL for the eat API
    BASE_URL: str = "https://api.lmu-dev.org"
    BASE_PREFIX_EAT: str = "/eat/v1"
    
    # API key for authentication our api
    API_KEY: str
    
    # Postgres database credentials
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str

    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()