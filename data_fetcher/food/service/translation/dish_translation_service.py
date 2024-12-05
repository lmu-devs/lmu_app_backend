from typing import List

from shared.core.logging import get_food_fetcher_logger
from shared.enums.language_enums import LanguageEnum
from shared.services.translation_service import TranslationService
from shared.tables.food.dish_table import DishTable, DishTranslationTable

logger = get_food_fetcher_logger(__name__)

class DishTranslationService:
    def __init__(self):
        self.translation_service = TranslationService()

    def create_translations(
        self,
        dish_obj: DishTable,
        source_dish: DishTranslationTable,
        target_languages: List[LanguageEnum],
        source_language: LanguageEnum = LanguageEnum.GERMAN
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
            translations.append(source_dish)
            
            # Create translations for each target language
            for target_lang in target_languages:
                if target_lang != source_language:
                    translated_name = self.translation_service.translate_text(
                        source_dish.title,
                        target_lang=target_lang.value
                    )
                    
                    if translated_name:
                        translation = DishTranslationTable(
                            dish_id=dish_obj.id,
                            language=target_lang.value,
                            title=translated_name
                        )
                        logger.info(f"Created translation for dish {dish_obj.id} to {target_lang.value}: {translated_name}")
                        translations.append(translation)
                    else:
                        logger.warning(
                            f"Failed to translate dish {dish_obj.id} to {target_lang.value}"
                        )
            
            return translations
            
        except Exception as e:
            logger.error(f"Failed to create translations for dish {dish_obj.id}: {str(e)}")
            raise