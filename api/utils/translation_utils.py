from typing import TypeVar, Any, Sequence

from sqlalchemy import Select, case, select
from sqlalchemy.orm import selectinload, contains_eager
from shared.core.language import Language
from shared.core.logging import get_api_logger
from shared.models.dish_model import DishTable
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
    logger.info(f"Getting translation for language: {language}")
    
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

def apply_translation_query(base_query : Select, model, translation_model, language: Language) -> Select:
    """
    Generic function to apply translation filtering logic to any query with translations.
    
    Args:
        base_query: The base SQLAlchemy select statement
        model: The main model class (e.g., DishTable, WishlistTable)
        translation_model: The translation model class (e.g., DishTranslationTable)
        language: Target language
    
    Returns:
        Modified query with translation filtering logic
    """
    return (
        base_query
        .join(model.translations)
        .filter(translation_model.language.in_([language.value, Language.GERMAN.value]))
        .options(
            contains_eager(model.translations)
        )
        .order_by(
            model.id,  # Ensure consistent ordering
            case(
                (translation_model.language == language.value, 1),
                (translation_model.language == Language.GERMAN.value, 2),
                else_=3
            )
        )
    )