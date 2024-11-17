from typing import Optional
from fastapi import Header
from enum import Enum

from shared.core.logging import get_api_logger

logger = get_api_logger(__name__)

class Language(str, Enum):
    GERMAN = "DE"
    ENGLISH_US = "EN-US"
    
    @classmethod
    def from_header(cls, header: str) -> "Language":
        """Convert HTTP Accept-Language header to Language enum"""
        logger.info(f"Converting Accept-Language header: {header}")
        header = header.upper()
        if header.startswith("DE"):
            return cls.GERMAN
        if header.startswith("EN"):
            return cls.ENGLISH_US  # Default to US English
        logger.warning(f"No supported language found in Accept-Language header: {header}")
        return cls.GERMAN  # Default fallback

async def get_language(
    accept_language: Optional[str] = Header(
        default=None,
        description="Preferred language (e.g., en-US, de-DE)"
    )
) -> Language:
    """
    FastAPI dependency that extracts the preferred language from the Accept-Language header.
    Falls back to German if no supported language is found.
    """
    if not accept_language:
        return Language.GERMAN
        
    return Language.from_header(accept_language)