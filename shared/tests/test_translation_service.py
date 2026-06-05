from uuid import uuid4

import pytest

from shared.src.enums import LanguageEnum
from shared.src.services import TranslationService
from shared.src.tables import DishTable, DishTranslationTable


class FakeTranslationResult:
    def __init__(self, text: str):
        self.text = text


class FakeTranslator:
    def translate_text(self, text: str, source_lang: str, target_lang: str):
        return FakeTranslationResult(f"{target_lang}: {text}")


class FailingTranslator:
    def translate_text(self, text: str, source_lang: str, target_lang: str):
        raise RuntimeError("DeepL unavailable")


@pytest.fixture
def translation_service():
    return TranslationService(translator=FakeTranslator())


def test_dish_translations_no_source(translation_service):
    # Create dish with no translations
    dish = DishTable(
        id=uuid4(),
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
        id=uuid4(),
        dish_type="Test Dish",
        dish_category="Test Category",
        labels=["Test Label"],
        price_simple="Test Price",
    )

    dish.translations = [DishTranslationTable(language=LanguageEnum.GERMAN.value, title="Grüner Salat")]

    translations = translation_service.create_missing_translations(dish)

    # Should only return newly created translations
    assert len(translations) == 1

    # English translation should exist
    eng_trans = next(t for t in translations if t.language == LanguageEnum.ENGLISH_US.value)
    assert eng_trans.title == "EN-US: Grüner Salat"


def test_no_duplicate_translations(translation_service):
    # Create dish with all translations
    dish = DishTable(
        id=uuid4(),
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
    assert translations == []


def test_translation_failure_raises_runtime_error():
    translation_service = TranslationService(translator=FailingTranslator())
    dish = DishTable(
        id=uuid4(),
        dish_type="Test Dish",
        dish_category="Test Category",
        labels=["Test Label"],
        price_simple="Test Price",
    )
    dish.translations = [DishTranslationTable(language=LanguageEnum.GERMAN.value, title="Grüner Salat")]

    with pytest.raises(RuntimeError, match="Translation failed from DE to EN-US"):
        translation_service.create_missing_translations(dish)
