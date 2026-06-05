from typing import Dict, List, Optional, Protocol, Set, Type, TypeVar

import deepl
from sqlalchemy import String
from sqlalchemy.inspection import inspect

from shared.src.core.logging import get_translation_logger
from shared.src.core.settings import get_settings
from shared.src.enums import LanguageEnum
from shared.src.tables.language_table import LanguageTable

logger = get_translation_logger(__name__)

T = TypeVar("T")  # Generic type for the main table
TransT = TypeVar("TransT", bound=LanguageTable)  # Generic type for translation table


class TranslationResult(Protocol):
    text: str


class Translator(Protocol):
    def translate_text(self, text: str, source_lang: str, target_lang: str) -> TranslationResult: ...


class TranslationService:
    """
    Creates missing language rows for models that follow the translation-table pattern.

    Expected parent model shape:
    - has an `id`
    - has a SQLAlchemy relationship named `translations`
    - that relationship points to a `LanguageTable` subclass
    - the translation table has one parent foreign key and string columns to translate
    """

    def __init__(self, translator: Optional[Translator] = None):
        if translator is None:
            settings = get_settings()
            translator = deepl.Translator(settings.DEEPL_API_KEY)
        self.translator = translator

    @staticmethod
    def _get_deepl_language_code(language: LanguageEnum, is_source: bool = False) -> str:
        """
        Convert app language codes to DeepL language codes.
        """
        code = language.value
        if is_source or language != LanguageEnum.ENGLISH_US:
            code = code.split("-")[0]
        return code.upper()

    def _translate_text(
        self,
        text: str,
        target_lang: LanguageEnum,
        source_lang: LanguageEnum = LanguageEnum.GERMAN,
    ) -> str:
        """
        Translate text using DeepL API
        """
        source_lang_code = TranslationService._get_deepl_language_code(source_lang, is_source=True)
        target_lang_code = TranslationService._get_deepl_language_code(target_lang)

        try:
            result = self.translator.translate_text(text, source_lang=source_lang_code, target_lang=target_lang_code)
            logger.info(f"Translated text from {source_lang_code} to {target_lang_code} " f"(characters={len(text)})")
            return result.text
        except Exception as e:
            logger.error(
                f"Translation failed from {source_lang_code} to {target_lang_code} "
                f"(characters={len(text)}): {str(e)}"
            )
            raise RuntimeError(f"Translation failed from {source_lang_code} to {target_lang_code}") from e

    def _get_translation_class(self, obj: T) -> Type[TransT]:
        """
        Get the translation class from the object's relationships
        Eg: LibraryTable -> LibraryTranslationTable
        """
        relationships = inspect(obj.__class__).relationships
        if "translations" in relationships.keys():
            return relationships["translations"].mapper.class_

        raise ValueError(f"No translations relationship found in {obj.__class__.__name__}")

    def _get_foreign_key_column(self, translation_table: Type[TransT]) -> str:
        """
        Get the foreign key column name from the translation table
        Eg: LibraryTranslationTable -> library_id
        """
        foreign_key_columns = []
        for column in inspect(translation_table).columns:
            has_parent_foreign_key = any(
                not foreign_key.column.table.name.startswith("language") for foreign_key in column.foreign_keys
            )
            if has_parent_foreign_key:
                foreign_key_columns.append(column.name)

        if len(foreign_key_columns) == 1:
            return foreign_key_columns[0]

        raise ValueError(
            f"Expected exactly one parent foreign key in translation table {translation_table.__name__}, "
            f"found {len(foreign_key_columns)}"
        )

    def _get_translatable_columns(self, translation_table: Type[TransT]) -> List[str]:
        """
        Get all string columns from the translation table except 'language'
        """
        return [
            column.name
            for column in inspect(translation_table).columns
            if (isinstance(column.type, String) and column.name != "language" and not column.primary_key)
        ]

    def _get_source_translation(self, obj: T, existing_translations: List[TransT]) -> tuple[TransT, LanguageEnum]:
        """
        Get the best source translation to translate from.
        Prefers English, then German, then first available translation.
        """
        for language in (LanguageEnum.ENGLISH_US, LanguageEnum.GERMAN):
            translation = next(
                (translation for translation in existing_translations if translation.language == language.value),
                None,
            )
            if translation:
                return translation, language

        if not existing_translations:
            raise ValueError(f"No existing translations found for table {obj.__tablename__} object {obj.id}")

        first_translation = existing_translations[0]
        return first_translation, LanguageEnum(first_translation.language)

    def _get_missing_languages(self, existing_translations: List[TransT]) -> List[LanguageEnum]:
        """
        Get the missing languages from the existing translations.
        Eg: existing: [de-DE, en-US], enum: [de-DE, en-US, fr-FR], return: [fr-FR]
        """
        existing_languages: Set[str] = {translation.language for translation in existing_translations}
        return [language for language in LanguageEnum if language.value not in existing_languages]

    def _create_translation(
        self,
        translation_class: Type[TransT],
        obj: T,
        source_translation: TransT,
        source_language: LanguageEnum,
        target_language: LanguageEnum,
        translatable_columns: List[str],
        foreign_key_name: str,
    ) -> TransT:
        translated_fields: Dict[str, object] = {
            foreign_key_name: obj.id,
            "language": target_language.value,
        }

        for column in translatable_columns:
            source_text = getattr(source_translation, column)
            translated_fields[column] = (
                None
                if source_text is None
                else self._translate_text(
                    source_text,
                    source_lang=source_language,
                    target_lang=target_language,
                )
            )

        return translation_class(**translated_fields)

    def create_missing_translations(
        self,
        obj: T,
    ) -> List[TransT]:
        """
        Creates translations for all missing languages for all translatable fields.
        Does not update partially filled existing translation rows.

        Args:
            obj: The object to translate

        Returns:
            List of newly created translation table objects
        """
        translation_class = self._get_translation_class(obj)
        existing_translations: List[TransT] = list(obj.translations)
        missing_languages = self._get_missing_languages(existing_translations)

        if not missing_languages:
            logger.info(f"Table {obj.__tablename__} object {obj.id} already has all required translations")
            return []

        source_translation, source_language = self._get_source_translation(obj, existing_translations)
        translatable_columns = self._get_translatable_columns(translation_class)
        foreign_key_name = self._get_foreign_key_column(translation_class)

        new_translations = [
            self._create_translation(
                translation_class,
                obj,
                source_translation,
                source_language,
                target_language,
                translatable_columns,
                foreign_key_name,
            )
            for target_language in missing_languages
        ]

        logger.info(f"Created {len(new_translations)} translations for table {obj.__tablename__} object {obj.id}")
        return new_translations
