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
            return cls.ENGLISH_US
        logger.warning(f"No supported language found in Accept-Language header: {header}")
        return cls.GERMAN  # Default fallback
