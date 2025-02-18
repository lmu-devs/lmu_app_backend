from collections.abc import Generator
from typing import Any, Literal, Protocol

import google.generativeai as genai
import instructor

# from anthropic import Anthropic
from google.generativeai import GenerativeModel
from openai import OpenAI
from pydantic import BaseModel

from shared.src.core.settings import AnthropicSettings, GeminiSettings, OpenAISettings, get_settings
from shared.src.models.llm_message_models import SystemMessage, UserMessage

type LLMProviders = Literal["openai", "anthropic", "gemini"]
type LLMSettings = OpenAISettings | AnthropicSettings | GeminiSettings


class ClientInitializerCallback(Protocol):
    def __call__(self, settings: LLMSettings) -> instructor.Instructor: ...


type ClientInitializer = dict[LLMProviders, ClientInitializerCallback]


class LLMFactory:
    def __init__(self, provider: LLMProviders, system_message: SystemMessage | None = None) -> None:
        self.provider: LLMProviders = provider
        self.system_message: SystemMessage | None = system_message
        self.settings: LLMSettings = getattr(get_settings(), provider)
        self.client: instructor.Instructor = self._initialize_client()

    def _initialize_client(self) -> instructor.Instructor:
        if self.provider == "gemini":
            genai.configure(api_key=self.settings.api_key)

        client_initializers: ClientInitializer = {
            "openai": lambda settings: instructor.from_openai(OpenAI(api_key=settings.api_key)),
            # "anthropic": lambda settings: instructor.from_anthropic(Anthropic(api_key=settings.api_key)),
            "gemini": lambda settings: instructor.from_gemini(GenerativeModel(
                model_name=settings.default_model,
                generation_config=settings.generation_config,
                system_instruction=getattr(self.system_message, "content", None),
            ),
                mode=instructor.Mode.GEMINI_JSON,
            ),
        }

        initializer = client_initializers.get(self.provider)
        if initializer:
            return initializer(self.settings)

        err_msg = f"Unsupported LLM provider: {self.provider}"
        raise ValueError(err_msg)

    def create_completion[T: type[BaseModel]](
        self,
        response_model: T,
        messages: list[dict[str, str]],
        **kwargs: Any,
    ) -> T | Generator[T, None, None]:
        # Konvertiere SystemMessage, HumanMessage und AIMessage in Dictionaries
        messages = [message.model_dump() for message in messages]

        if self.provider != "gemini":
            if self.system_message:
                messages.insert(0, self.system_message.model_dump())
            completion_params = {
                "temperature": kwargs.get("temperature", self.settings.temperature),
                "max_retries": kwargs.get("max_retries", self.settings.max_retries),
                "max_tokens": kwargs.get("max_tokens", self.settings.max_tokens),
                "model": kwargs.get("model", self.settings.default_model),
                "response_model": response_model,
                "messages": messages,
            }
            return self.client.chat.completions.create(**completion_params)
        else:
            return self.client.chat.completions.create(
                messages=messages,
                response_model=response_model,
            )

    
    
if __name__ == "__main__":

    class CompletionResponse(BaseModel):
        response: str

    llm_factory = LLMFactory(provider="openai")
    completion = llm_factory.create_completion(
        response_model=CompletionResponse,
        messages=[
            # SystemMessage(content="You are a helpful assistant that generates aliases for a given name."),
            UserMessage(content="Hey how are you?"),
        ],
    )
    print(completion)