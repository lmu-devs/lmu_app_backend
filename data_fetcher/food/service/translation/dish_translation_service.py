from typing import List, Set

from shared.core.logging import get_food_fetcher_logger
from shared.enums.language_enums import LanguageEnum
from shared.services.translation_service import TranslationService
from shared.tables.food.dish_table import DishTable, DishTranslationTable
from shared.tables.language_table import LanguageTable

logger = get_food_fetcher_logger(__name__)

class DishTranslationService:
    def __init__(self):
        self.translation_service = TranslationService()
        
    def translate_all_dishes(self, dishes: List[DishTable], target_languages: List[LanguageEnum]):
        """
        Translate all dishes to missing target languages
        """
        for dish in dishes:
            self.create_missing_translations(dish, target_languages)

    def get_source_translation(
        self,
        dish_obj: DishTable,
        existing_translations: List[DishTranslationTable]
    ) -> tuple[DishTranslationTable, LanguageEnum]:
        """
        Get the best source translation to translate from.
        Prefers English, then German, then first available translation.
        
        Returns:
            Tuple of (source_translation, source_language)
        """
        # Try to find English translation first
        eng_trans = next(
            (t for t in existing_translations if t.language == LanguageEnum.ENGLISH_US.value),
            None
        )
        if eng_trans:
            return eng_trans, LanguageEnum.ENGLISH_US

        # Try German next
        de_trans = next(
            (t for t in existing_translations if t.language == LanguageEnum.GERMAN.value),
            None
        )
        if de_trans:
            return de_trans, LanguageEnum.GERMAN

        # Fall back to first available translation
        if existing_translations:
            first_trans = existing_translations[0]
            source_lang = next(
                lang for lang in LanguageEnum 
                if lang.value == first_trans.language
            )
            return first_trans, source_lang

        raise ValueError(f"No existing translations found for dish {dish_obj.id}")

    def create_missing_translations(
        self,
        dish_obj: DishTable,
    ) -> List[DishTranslationTable]:
        """
        Creates translations only for missing target languages.
        
        Args:
            dish_obj: The dish object to translate
            target_languages: List of Language enum values to translate to
            
        Returns:
            List of created DishTranslationTable objects
        """
        try:
            # Get existing translations
            existing_translations : List[LanguageTable] = list(dish_obj.translations)
            existing_languages : Set[str] = {trans.language for trans in existing_translations}
            
            # Find languages that need translation
            target_languages = [language for language in LanguageEnum]
            missing_languages = [
                lang for lang in target_languages 
                if lang.value not in existing_languages
            ]
            
            if not missing_languages:
                logger.info(f"Dish {dish_obj.id} already has all required translations")
                return existing_translations

            # Get source translation
            source_translation, source_language = self.get_source_translation(
                dish_obj, 
                existing_translations
            )
            
            # Create translations for each missing language
            new_translations = []
            for target_lang in missing_languages:
                translated_name = self.translation_service.translate_text(
                    source_translation.title,
                    source_lang=source_language,
                    target_lang=target_lang
                )
                
                if translated_name:
                    translation = DishTranslationTable(
                        dish_id=dish_obj.id,
                        language=target_lang.value,
                        title=translated_name
                    )
                    logger.info(f"Created translation for dish {dish_obj.id} to {target_lang.value}: {translated_name}")
                    new_translations.append(translation)
                else:
                    logger.warning(
                        f"Failed to translate dish {dish_obj.id} to {target_lang.value}"
                    )
            
            return existing_translations + new_translations
            
        except Exception as e:
            logger.error(f"Failed to create translations for dish {dish_obj.id}: {str(e)}")
            raise


if __name__ == "__main__":
    # create fake dish object with dish translations
    dish = DishTable(dish_type="Test Dish", dish_category="Test Category", labels=["Test Label"], price_simple="Test Price", translations=[DishTranslationTable(language=LanguageEnum.SPANISH.value, title="Ensalada Verde")])
    
    print(dish.__dict__)
    
    test = DishTranslationService()
    translations = test.create_missing_translations(dish)
    
    print([t.__dict__ for t in translations])
    
    