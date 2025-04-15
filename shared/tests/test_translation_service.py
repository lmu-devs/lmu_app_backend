import pytest

from shared.src.enums import LanguageEnum
from shared.src.services import TranslationService
from shared.src.tables import (
    DishTable,
    DishTranslationTable,
    WishlistStatus,
    WishlistTable,
    WishlistTranslationTable,
)


@pytest.fixture
def translation_service():
    return TranslationService()


def test_wishlist_translations(translation_service):
    # Create test wishlist with one translation
    wishlist = WishlistTable(
        status=WishlistStatus.DEVELOPMENT,
        translations=[
            WishlistTranslationTable(
                language=LanguageEnum.ENGLISH_US.value,
                title="My Wishlist",
                description="This is my wishlist",
            )
        ],
    )

    translations = translation_service.create_missing_translations(wishlist)

    # Should create translations for all languages
    assert len(translations) == len(LanguageEnum)

    german_trans = next(t for t in translations if t.language == LanguageEnum.GERMAN.value)
    assert german_trans.title is not None
    assert german_trans.description is not None


def test_dish_translations_no_source(translation_service):
    # Create dish with no translations
    dish = DishTable(
        id=1,
        dish_type="Test Dish",
        dish_category="Test Category",
        labels=["Test Label"],
        price_simple="Test Price",
    )

    # Should raise error with no source translation
    with pytest.raises(ValueError):
        translation_service.create_missing_translations(dish)


def test_dish_translations_with_source(translation_service):
    # Create dish with German translation
    dish = DishTable(
        id=1,
        dish_type="Test Dish",
        dish_category="Test Category",
        labels=["Test Label"],
        price_simple="Test Price",
    )

    dish.translations = [DishTranslationTable(language=LanguageEnum.GERMAN.value, title="Grüner Salat")]

    translations = translation_service.create_missing_translations(dish)

    # Should create translations for all languages
    assert len(translations) == len(LanguageEnum)

    # English translation should exist
    eng_trans = next(t for t in translations if t.language == LanguageEnum.ENGLISH_US.value)
    assert eng_trans.title is not None


def test_no_duplicate_translations(translation_service):
    # Create dish with all translations
    dish = DishTable(
        id=1,
        dish_type="Test Dish",
        dish_category="Test Category",
        labels=["Test Label"],
        price_simple="Test Price",
    )

    # Add translations for all languages
    dish.translations = [
        DishTranslationTable(language=lang.value, title=f"Title in {lang.value}") for lang in LanguageEnum
    ]

    translations = translation_service.create_missing_translations(dish)

    # Should not create any new translations
    assert len(translations) == len(LanguageEnum)
    assert all(t.title.startswith("Title in") for t in translations)
