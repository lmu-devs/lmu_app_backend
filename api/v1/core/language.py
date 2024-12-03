from typing import Optional

from fastapi import Header

from shared.enums.language_enums import LanguageEnum


async def get_language(
    accept_language: Optional[str] = Header(
        default=LanguageEnum.GERMAN,
        description="Supported languages (en, de)",
        enum=[lang.value for lang in LanguageEnum]
    )
) -> LanguageEnum:
    """
    FastAPI dependency that extracts the preferred language from the Accept-Language header.
    Falls back to German if no supported language is found.
    """ 
    return LanguageEnum.from_header(accept_language)