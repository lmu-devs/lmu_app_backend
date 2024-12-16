# Example usage
import pytest
from shared.enums.language_enums import LanguageEnum
from shared.services.translation_service import TranslationService
from shared.tables.food.dish_table import DishTable, DishTranslationTable
from shared.tables.wishlist_table import WishlistTable, WishlistTranslationTable


if __name__ == "__main__":
    
    translation_service = TranslationService()
    
    # ============================
    # Create test wishlist with one translation
    wishlist = WishlistTable(
        status="DEVELOPMENT",
        translations=[
            WishlistTranslationTable(
                language=LanguageEnum.ENGLISH_US.value,
                title="My Wishlist",
                description="This is my wishlist"
            )
        ]
    )
    
    translations = translation_service.create_missing_translations(wishlist)
    
    # Print results
    for trans in translations:
        print(f"Language: {trans.language}")
        print(f"Title: {trans.title}")
        print(f"Description: {trans.description}")
        print("---\n")

  
    # ============================
    # Create fake dish object with dish translations
    dish = DishTable(
        id=1,
        dish_type="Test Dish", 
        dish_category="Test Category", 
        labels=["Test Label"], 
        price_simple="Test Price", 
    )
    # Test if there is no source translation, should raise error
    with pytest.raises(ValueError):
        translations = translation_service.create_missing_translations(dish)
    
    dish.translations = [
        DishTranslationTable(
            language=LanguageEnum.GERMAN.value, 
            title="Grüner Salat"
        )
    ]
    
    print(dish.__dict__)
    
    translations = translation_service.create_missing_translations(dish)
    assert len(translations) == len(LanguageEnum)
    print([t.__dict__ for t in translations])
    
    
    # Service shouldnt update translations if they already exist
    dish.translations = translations
    translations = translation_service.create_missing_translations(dish)
    assert len(translations) == len(LanguageEnum)
    # ============================
    
    