from typing import Any, Dict, List, Optional, Set, Type, TypeVar

import deepl
from sqlalchemy import String
from sqlalchemy.inspection import inspect
from sqlalchemy.orm.relationships import RelationshipProperty

from shared.src.core.logging import get_translation_logger
from shared.src.core.settings import get_settings
from shared.src.enums import LanguageEnum
from shared.src.tables.language_table import LanguageTable

logger = get_translation_logger(__name__)

T = TypeVar("T")  # Generic type for the main table
TransT = TypeVar("TransT", bound=LanguageTable)  # Generic type for translation table


class TranslationService:
    def __init__(self):
        settings = get_settings()
        self.translator = deepl.Translator(settings.DEEPL_API_KEY)

    def _translate_text(self, text: str, target_lang: str, source_lang: str = LanguageEnum.GERMAN) -> Optional[str]:
        """
        Translate text using DeepL API
        """
        try:
            source_lang = source_lang.value
            target_lang = target_lang.value

            # convert target_lang to deepl language code, only if source_lang is English
            # https://developers.deepl.com/docs/resources/supported-languages
            target_lang = target_lang.split("-")[0] if target_lang != LanguageEnum.ENGLISH_US.value else target_lang
            source_lang = source_lang.split("-")[0]

            source_lang = source_lang.upper()
            target_lang = target_lang.upper()

            result = self.translator.translate_text(text, source_lang=source_lang, target_lang=target_lang)
            logger.info(f"Translated {source_lang}: {text} • to {target_lang}: {result.text}")
            return result.text
        except Exception as e:
            logger.error(f"Translation failed for {text} to {target_lang}: {str(e)}")
            return None

    def _get_translation_class(self, obj: T) -> Type[TransT]:
        """
        Get the translation class from the object's relationships
        """
        mapper = inspect(obj.__class__)
        for rel in mapper.relationships:
            if isinstance(rel, RelationshipProperty):
                # Look for the translations relationship
                if rel.key == "translations":
                    return rel.mapper.class_
        raise ValueError(f"No translations relationship found in {obj.__class__.__name__}")

    def _get_foreign_key_column(self, translation_table: Type[TransT]) -> str:
        """
        Get the foreign key column name from the translation table
        """
        for column in inspect(translation_table).columns:
            if isinstance(column.foreign_keys, set) and len(column.foreign_keys) > 0:
                for fk in column.foreign_keys:
                    if not fk.column.table.name.startswith("language"):
                        return column.name
        raise ValueError(f"No foreign key column found in translation table {translation_table.__name__}")

    def _get_translatable_columns(self, translation_table: Type[TransT]) -> List[str]:
        """
        Get all string columns from the translation table except 'language'
        """
        columns = []
        for column in inspect(translation_table).columns:
            if isinstance(column.type, String) and column.name != "language" and not column.primary_key:
                columns.append(column.name)
        return columns

    def _get_source_translation(self, obj: T, existing_translations: List[TransT]) -> tuple[TransT, LanguageEnum]:
        """
        Get the best source translation to translate from.
        Prefers English, then German, then first available translation.
        """
        # Try to find English translation first
        eng_trans = next(
            (t for t in existing_translations if t.language == LanguageEnum.ENGLISH_US.value),
            None,
        )
        if eng_trans:
            return eng_trans, LanguageEnum.ENGLISH_US

        # Try German next
        de_trans = next(
            (t for t in existing_translations if t.language == LanguageEnum.GERMAN.value),
            None,
        )
        if de_trans:
            return de_trans, LanguageEnum.GERMAN

        # Fall back to first available translation
        if existing_translations:
            first_trans = existing_translations[0]
            source_lang = next(lang for lang in LanguageEnum if lang.value == first_trans.language)
            return first_trans, source_lang

        logger.error(f"No existing translations found for table {obj.__tablename__} object {obj.id}")
        raise ValueError(f"No existing translations found for table {obj.__tablename__} object {obj.id}")

    def create_missing_translations(
        self,
        obj: T,
    ) -> List[TransT]:
        """
        Creates translations for all missing languages for all translatable fields.

        Args:
            obj: The object to translate

        Returns:
            List of created translation table objects
        """
        try:
            # Get translation class and existing translations
            translation_class = self._get_translation_class(obj)
            existing_translations: List[LanguageTable] = list(obj.translations)
            existing_languages: Set[str] = {trans.language for trans in existing_translations}

            # Find languages that need translation
            target_languages = [language for language in LanguageEnum]
            missing_languages = [lang for lang in target_languages if lang.value not in existing_languages]

            if not missing_languages:
                logger.info(f"Table {obj.__tablename__} object {obj.id} already has all required translations")
                return existing_translations

            # Get source translation and translatable columns
            source_translation, source_language = self._get_source_translation(obj, existing_translations)
            translatable_columns = self._get_translatable_columns(translation_class)
            foreign_key_name = self._get_foreign_key_column(translation_class)

            # Create translations for each missing language
            new_translations = []
            for target_lang in missing_languages:
                # Translate all translatable fields
                translated_fields: Dict[str, Any] = {
                    foreign_key_name: obj.id,
                    "language": target_lang.value,
                }

                for column in translatable_columns:
                    source_text = getattr(source_translation, column)
                    translated_text = self._translate_text(
                        source_text,
                        source_lang=source_language,
                        target_lang=target_lang,
                    )
                    translated_fields[column] = translated_text

                translation = translation_class(**translated_fields)
                logger.info(f"Created translation for table {obj.__tablename__} object {obj.id} to {target_lang.value}")
                new_translations.append(translation)

            return existing_translations + new_translations

        except Exception as e:
            logger.error(f"Failed to create translations for table {obj.__tablename__} object {obj.id}: {str(e)}")
            raise

    def get_translation(self, obj: T, language: LanguageEnum) -> Optional[TransT]:
        """
        Get translation for a specific language from an object's translations

        Args:
            obj: The object containing translations
            language: The target language to get translation for

        Returns:
            Translation object if found, None otherwise
        """
        try:
            return next((t for t in obj.translations if t.language == language.value), None)
        except Exception as e:
            logger.error(f"Failed to get {language.value} translation for {obj.__class__.__name__} {obj.id}: {str(e)}")
            return None
