from sqlalchemy import Select, case
from sqlalchemy.orm import contains_eager

from shared.src.enums import LanguageEnum


def apply_translation_query(base_query: Select, model, translation_model, language: LanguageEnum) -> Select:
    """
    Generic function to apply translation filtering logic to any query with translations.
    """
    return (
        base_query
        .outerjoin(model.translations)
        .options(
            contains_eager(model.translations)
        )
        .order_by(
            model.id,  # Ensure consistent ordering
            case(
                (translation_model.language == language.value, 1),
                (translation_model.language == LanguageEnum.GERMAN.value, 2),
                else_=3
            )
        )
    )
    
def create_translation_order_case(translation_table, language: LanguageEnum):
    """Helper function to create consistent translation ordering cases"""
    return case(
        (translation_table.language == language.value, 1),
        (translation_table.language == LanguageEnum.GERMAN.value, 2),
        else_=3
    )