from enum import Enum

from shared.src.core.logging import get_food_logger

logger = get_food_logger(__name__)


class LanguageEnum(str, Enum):
    GERMAN = "de-DE"
    ENGLISH_US = "en-US"

    @classmethod
    def from_header(cls, header: str) -> "LanguageEnum":
        """Convert HTTP Accept-Language header to Language enum"""
        logger.info(f"Converting Accept-Language header: {header}")
        header = header.upper()
        if header.startswith("DE"):
            return cls.GERMAN
        if header.startswith("EN"):
            return cls.ENGLISH_US
        logger.warning(f"No supported language found in Accept-Language header: {header}")
        return cls.GERMAN  # Default fallback
