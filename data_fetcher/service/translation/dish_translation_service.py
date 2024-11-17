from typing import List
from sqlalchemy.orm import Session
from shared.models.dish_model import DishTable, DishTranslationTable
from shared.core.language import Language
from shared.services.translation_service import TranslationService
from shared.core.logging import get_data_fetcher_logger

logger = get_data_fetcher_logger(__name__)

class DishTranslationService:
    def __init__(self, db: Session):
        self.db = db
        self.translation_service = TranslationService()

    def create_translations(
        self,
        dish_obj: DishTable,
        target_languages: List[Language],
        source_language: Language = Language.GERMAN
    ) -> List[DishTranslationTable]:
        """
        Creates translations for a dish in specified target languages.
        
        Args:
            dish_obj: The dish object to translate
            target_languages: List of Language enum values to translate to
            source_language: Source language (defaults to German)
            
        Returns:
            List of created DishTranslationTable objects
        """
        try:
            translations = []
            
            # Add source language translation
            source_translation = DishTranslationTable(
                dish_id=dish_obj.id,
                language=source_language.value,
                name=dish_obj.name
            )
            self.db.add(source_translation)
            translations.append(source_translation)
            
            # Create translations for each target language
            for target_lang in target_languages:
                if target_lang != source_language:
                    translated_name = self.translation_service.translate_text(
                        dish_obj.name,
                        target_lang=target_lang.value
                    )
                    
                    if translated_name:
                        translation = DishTranslationTable(
                            dish_id=dish_obj.id,
                            language=target_lang.value,
                            name=translated_name
                        )
                        logger.info(f"Created translation for dish {dish_obj.id} to {target_lang.value}: {translated_name}")
                        self.db.add(translation)
                        translations.append(translation)
                    else:
                        logger.warning(
                            f"Failed to translate dish {dish_obj.id} to {target_lang.value}"
                        )
            
            return translations
            
        except Exception as e:
            logger.error(f"Failed to create translations for dish {dish_obj.id}: {str(e)}")
            raise