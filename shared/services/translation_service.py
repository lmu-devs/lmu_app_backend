from typing import Optional

import deepl

from shared.core.logging import setup_logger
from shared.enums.language_enums import LanguageEnum
from shared.settings import get_settings

logger = setup_logger(__name__, "translation")

class TranslationService:
    def __init__(self):
        settings = get_settings()
        self.translator = deepl.Translator(settings.DEEPL_API_KEY)
        
    def translate_text(self, text: str, target_lang: str, source_lang: str = LanguageEnum.GERMAN) -> Optional[str]:
        """
        Translate text using DeepL API
        """
        try:
            # convert LanguageEnum.value 
            source_lang = source_lang.value
            target_lang = target_lang.value
            
            # convert target_lang to deepl language code, only if source_lang is English
                # https://developers.deepl.com/docs/resources/supported-languages
            print("splitting")
            source_lang = source_lang.split("-")[0] if source_lang != LanguageEnum.ENGLISH_US.value else source_lang
            target_lang = target_lang.split("-")[0] if target_lang != LanguageEnum.ENGLISH_US.value else target_lang
                
            source_lang = source_lang.upper()
            target_lang = target_lang.upper()
            
            print(f"source_lang: {source_lang}, target_lang: {target_lang}")
            
            result = self.translator.translate_text(text, 
                                                 source_lang=source_lang,
                                                 target_lang=target_lang)
            logger.info(f"Translated {text} to {target_lang}: {result.text}")
            return result.text
        except Exception as e:
            logger.error(f"Translation failed for {text} to {target_lang}: {str(e)}")
            return None 