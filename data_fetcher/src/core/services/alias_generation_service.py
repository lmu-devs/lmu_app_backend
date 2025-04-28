from typing import List

from pydantic import BaseModel, Field

from shared.src.models.llm_message_models import SystemMessage, UserMessage
from shared.src.services.llm_service import LLMService


class AliasGenerationResponse(BaseModel):
    aliases: List[str] = Field(
        description="A list of fitting aliases that helps the user to find the given input in a search box",
        min_items=2,
        max_items=7,
    )


class AliasGenerationService:
    def __init__(self, llm_factory: LLMService | None = None):
        system_message = SystemMessage(
            content="""You are a helpful assistant that generates aliases for a given input. 
            Be sensitive to the language of the input and generate aliases in the same language.
            Think of FITTING, SIMPLE and SINGE WORD search terms a student
            would use to find the given input. DONT REPEAT SIMILAR ALIASES. 
            SINGLE WORDS ONLY. DONT USE CAMEL CASE. NO "lmu", "munich", "student", "university" in the aliases.
            """
        )
        self.llm_factory = llm_factory or LLMService(provider="openai", system_message=system_message)

    def generate_alias(self, content: str, context: str | None = None) -> AliasGenerationResponse:
        context = f"This is the context: {context}" if context else ""
        return self.llm_factory.create_completion(
            response_model=AliasGenerationResponse,
            model="gpt-4o-mini",
            messages=[
                UserMessage(content=context),
            ],
        )


if __name__ == "__main__":
    alias_generation_service = AliasGenerationService()
    print(
        alias_generation_service.generate_alias(
            "LMU Kino", "This is the context: LMU Kino is a movie theater at LMU Munich"
        )
    )
    print(
        alias_generation_service.generate_alias(
            "Hochschulsport",
            "This is the context: Hochschulsport is a sports club at LMU Munich",
        )
    )
    print(
        alias_generation_service.generate_alias(
            "Raumfinder",
            "This is the context: Raumfinder is a room finder at LMU Munich",
        )
    )
    print(
        alias_generation_service.generate_alias(
            "Benutzerkonto",
            "This is the context: Benutzerkonto is a user account at LMU Munich",
        )
    )
