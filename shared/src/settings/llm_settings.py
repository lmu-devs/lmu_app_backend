from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")
    max_tokens: int | None = None


class OpenAIConfig(LLMProviderSettings):
    api_key: str | None = Field(alias="OPENAI_API_KEY", default=None)
    default_model: str = "gpt-4o"
    temperature: float = 0.7


class AnthropicConfig(LLMProviderSettings):
    api_key: str | None = Field(alias="ANTHROPIC_API_KEY", default=None)
    default_model: str = "claude-3-5-sonnet-20240620"
    max_tokens: int | None = 1024
