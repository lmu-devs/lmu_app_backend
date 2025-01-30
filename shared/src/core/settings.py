from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    # Base URL for the eat API
    API_BASE_URL: str = "https://api.lmu-dev.org"
    API_V1_PREFIX: str = "/v1"
    API_V1_PREFIX_FOOD: str = f"{API_V1_PREFIX}/food"
    API_V1_PREFIX_CINEMA: str = f"{API_V1_PREFIX}/cinema"
    
    # Base URL for the images
    IMAGES_BASE_URL: str = f"{API_BASE_URL}/images"
    IMAGES_BASE_URL_CANTEENS: str = f"{IMAGES_BASE_URL}/canteens"
    IMAGES_BASE_URL_DISHES: str = f"{IMAGES_BASE_URL}/dishes"
    IMAGES_BASE_URL_CINEMAS: str = f"{IMAGES_BASE_URL}/cinemas"
    
    # API key for authentication our api
    SYSTEM_API_KEY: str
    ADMIN_API_KEY: str
    
    # API keys for external services
    DEEPL_API_KEY: str
    TMDB_API_KEY: str
    OMDB_API_KEY: str
    
    TELEGRAM_BOT_TOKEN: str 
    TELEGRAM_CHAT_ID: str 
    
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
    
    class ConfigDict:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()