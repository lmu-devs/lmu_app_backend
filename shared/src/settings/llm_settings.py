from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from google.generativeai.types import GenerationConfig

class LLMProviderSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    temperature: float = 0.0
    max_tokens: int | None = None
    max_retries: int = 3


class OpenAISettings(LLMProviderSettings):
    api_key: str | None = Field(alias="OPENAI_API_KEY", default=None)
    default_model: str = "gpt-4o"


class AnthropicSettings(LLMProviderSettings):
    api_key: str | None = Field(alias="ANTHROPIC_API_KEY", default=None)
    default_model: str = "claude-3-5-sonnet-20240620"
    max_tokens: int | None = 1024


class GeminiSettings(LLMProviderSettings):
    api_key: str | None = Field(alias="GEMINI_API_KEY", default=None)
    default_model: str = "gemini-2.0-flash-lite-preview-02-05"
    generation_config: GenerationConfig = GenerationConfig(
        max_output_tokens=1024,
    )
