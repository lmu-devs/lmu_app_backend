from typing import Optional
from fastapi import Header

from shared.core.language import Language

async def get_language(
    accept_language: Optional[str] = Header(
        default=Language.GERMAN,
        description="Supported languages (en, de)",
        enum=[lang.value for lang in Language]
    )
) -> Language:
    """
    FastAPI dependency that extracts the preferred language from the Accept-Language header.
    Falls back to German if no supported language is found.
    """ 
    return Language.from_header(accept_language)