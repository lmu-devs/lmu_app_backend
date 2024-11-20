from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    # Base URL for the eat API
    API_BASE_URL: str = "https://api.lmu-dev.org"
    API_V1_BASE_PREFIX: str = "/v1"
    API_V1_BASE_PREFIX_EAT: str = f"{API_V1_BASE_PREFIX}/eat"
    
    # API key for authentication our api
    SYSTEM_API_KEY: str
    ADMIN_API_KEY: str
    # Postgres database credentials
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str
    POSTGRES_HOST: str
    
    # PgAdmin settings
    PGADMIN_PORT: str = "5050"
    PGADMIN_DEFAULT_EMAIL: str
    PGADMIN_DEFAULT_PASSWORD: str
    
    DEEPL_API_KEY: str

    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()