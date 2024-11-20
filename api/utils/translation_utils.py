from typing import TypeVar, Any, Sequence
from shared.core.language import Language
from shared.core.logging import get_api_logger
logger = get_api_logger(__name__)

T = TypeVar('T')

def get_translation(
    translations: Sequence[T],
    language: Language,
    language_getter: callable,
    value_getter: callable
) -> Any:
    """
    Generic translation getter for any translatable entity.
    
    Args:
        translations: Sequence of translation objects
        language: Target language
        language_getter: Function to get language from translation object
        value_getter: Function to get desired value from translation object
    
    Returns:
        Translated value or "not translated" if no translation found
    """
    default_value = "not translated"
    
    # Try to find translation in requested language
    translation = next(
        (t for t in translations if language_getter(t) == language.value),
        None
    )
    
    # If not found, try German
    if not translation and language != Language.GERMAN:
        translation = next(
            (t for t in translations if language_getter(t) == Language.GERMAN.value),
            None
        )
    
    # If still not found, use first available translation
    if not translation and translations:
        translation = translations[0]
    
    # Use translation if found
    if translation:
        return value_getter(translation)
        
    return default_value 