from typing import List

from pydantic import BaseModel, Field

from shared.src.factories.llm_factory import LLMFactory
from shared.src.models.llm_message_models import SystemMessage, UserMessage


class AliasGenerationResponse(BaseModel):
    aliases: List[str] = Field(description="A list of fitting aliases that helps the user to find the given input in a search box",
                               min_items=2,
                               max_items=10,
                               )


class AliasGenerationService:
    def __init__(self, llm_factory: LLMFactory | None = None):
        system_message = SystemMessage(content="You are a helpful assistant that generates aliases for a given input. Try to be creative and think of simple and SINGE WORD search terms that a user would use to find the given input. DONT REPEAT SIMILAR ALIASES. SINGLE WORDS ONLY. DONT USE CAMEL CASE.")
        self.llm_factory = llm_factory or LLMFactory(provider='gemini', system_message=system_message)

    def generate_alias(self, content: str, context: str) -> AliasGenerationResponse:
        context = f"This is the context: {context}" if context else ""
        return self.llm_factory.create_completion(
            response_model=AliasGenerationResponse,
            model="gpt-3.5-turbo",
            messages=[
                UserMessage(content=context),
                UserMessage(content=content),
            ],
        )


if __name__ == "__main__":
    alias_generation_service = AliasGenerationService()
    print(alias_generation_service.generate_alias("LMU Kino"))
    print(alias_generation_service.generate_alias("Hochschulsport"))
    print(alias_generation_service.generate_alias("Raumfinder"))
    print(alias_generation_service.generate_alias("Benutzerkonto"))
    
