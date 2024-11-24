from sqlalchemy import Select, case
from sqlalchemy.orm import contains_eager

from shared.enums.language_enums import Language


def apply_translation_query(base_query: Select, model, translation_model, language: Language) -> Select:
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
                (translation_model.language == Language.GERMAN.value, 2),
                else_=3
            )
        )
    )