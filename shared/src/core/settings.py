from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from shared.src.settings.llm_settings import AnthropicConfig, OpenAIConfig


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "LMU App Backend"
    openai_config: OpenAIConfig = OpenAIConfig()
    anthropic_config: AnthropicConfig = AnthropicConfig()

    # Environment
    ENVIRONMENT: str

    # Deployment
    DOCKER_USERNAME: str

    # Base URL for the eat API
    API_BASE_URL: str = "https://api.lmu-dev.org"
    API_V1_PREFIX: str = "/v1"
    API_V2_PREFIX: str = "/v2"
    MIN_APP_VERSION: str = "1.0.0"

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

    # # Metabase settings
    # MB_DB_DBNAME: str
    # MB_DB_USER: str
    # MB_DB_PASSWORD: str
    # MB_DB_HOST: str
    # MB_DB_PORT: str

    # MB_EMAIL: str
    # MB_PASSWORD: str

    # Firebase
    FIREBASE_CREDENTIALS: str

    # AI Keys
    OPENAI_API_KEY: str

    # CMS
    DIRECTUS_ACCESS_TOKEN: str
    DIRECTUS_BASE_URL: str = Field(
        default="https://cms.lmu-dev.org",
        description="Using internal docker container for production (http://directus:8055)",
    )
    DIRECTUS_EXTERNAL_URL: str = "https://cms.lmu-dev.org"

    class ConfigDict:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
