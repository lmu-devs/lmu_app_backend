from typing import Generic, Literal, TypeVar

import litellm
from pydantic import BaseModel

from shared.src.core.settings import get_settings
from shared.src.models.llm_message_models import Message, SystemMessage, UserMessage
from shared.src.settings.llm_settings import AnthropicConfig, OpenAIConfig

LLMProviders = Literal["openai", "anthropic"]
LLMSettings = OpenAIConfig | AnthropicConfig
T = TypeVar("T", bound=BaseModel)


class LLMService(Generic[T]):
    def __init__(
        self,
        provider: LLMProviders,
        system_message: SystemMessage | None = None,
        model: str | None = None,
    ) -> None:
        self.provider = provider
        self.system_message = system_message
        self.settings = getattr(get_settings(), f"{provider}_config")
        self.model = self._normalize_model_name(model or self.settings.default_model)

    def _normalize_model_name(self, model: str) -> str:
        """Normalize the model name by adding provider prefix if needed."""
        if "/" not in model:
            return f"{self.provider}/{model}"
        return model

    def _prepare_messages(self, messages: list[Message], response_model: type[T]) -> list[dict]:
        """Prepare messages including system message and JSON formatting instructions."""
        prepared_messages = [msg.model_dump() for msg in messages]

        system_content = []
        if self.system_message:
            system_content.append(self.system_message.content)

        # Add JSON formatting instruction for OpenAI
        if self.provider == "openai":
            schema_str = response_model.model_json_schema()
            system_content.append(f"You must respond with a JSON object that matches this schema: {schema_str}")

        if system_content:
            prepared_messages.insert(0, {"role": "system", "content": " ".join(system_content)})

        return prepared_messages

    def create_completion(
        self,
        response_model: type[T],
        messages: list[Message],
        model: str | None = None,  # Added model parameter
        temperature: float | None = None,
        max_tokens: int | None = None,
        stream: bool = False,
    ) -> T:
        """Create a completion with the specified response model."""

        messages = self._prepare_messages(messages, response_model)

        # Use completion-specific model if provided, otherwise use factory model
        current_model = self._normalize_model_name(model) if model else self.model

        # Base completion parameters
        params = {
            "model": current_model,
            "messages": messages,
            "api_key": self.settings.api_key,
            "temperature": temperature or self.settings.temperature,
            "max_tokens": max_tokens or self.settings.max_tokens,
            "stream": stream,
        }

        if self.provider == "openai" and response_model:
            params["response_format"] = {"type": "json_object"}
            # print(response_model.model_json_schema())

        try:
            response = litellm.completion(**{k: v for k, v in params.items() if v is not None})
            return response_model.model_validate_json(response.choices[0].message.content)
        except Exception as e:
            print(f"LLM completion error: {e}")
            raise


# Example usage
if __name__ == "__main__":

    class CompletionResponse(BaseModel):
        response: str

    try:
        # Create factory with default model
        factory = LLMService[CompletionResponse](
            provider="openai",
            system_message=SystemMessage(content="Be concise and accurate."),
            model="gpt-4o-mini",  # Default model
        )

        # Use factory's default model
        result1 = factory.create_completion(
            response_model=CompletionResponse,
            messages=[UserMessage(content="What is 2+2?")],
        )
        print("Response with default model:", result1)

        # Override model for specific completion
        result2 = factory.create_completion(
            response_model=CompletionResponse,
            messages=[UserMessage(content="What is 3+3?")],
            model="gpt-4.1-nano",  # Override model for this completion
        )
        print("Response with overridden model:", result2)

    except Exception as e:
        print(f"Error during example run: {e}")
