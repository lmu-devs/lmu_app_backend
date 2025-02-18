from pydantic import BaseModel
from typing import List

from shared.src.enums import LanguageEnum

class LinkTranslationConstants(BaseModel):
    language: LanguageEnum
    title: str
    description: str
    alias: List[str]
    
class LinkConstants(BaseModel):
    url: str
    icon: str | None = None
    tags: List[str]
    translations: LinkTranslationConstants