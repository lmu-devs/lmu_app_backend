from pathlib import Path

from shared.src.core.settings import get_settings
from shared.src.enums.language_enums import LanguageEnum
from shared.src.services.directus_service import DirectusService


class LinkBenefitService:
    def __init__(self, language: LanguageEnum = LanguageEnum.GERMAN):
        self.language = language
        self.settings = get_settings()
        self.directus = DirectusService()

    async def get_benefits(self):
        try:
            query_path = Path(__file__).parent.parent / "graphql" / "link_benefits_query.graphql"
            response = self.directus.execute_query_file(
                query_file_path=query_path,
                variables={"languageCode": self.language.value},
            )
            return response
        except Exception as e:
            raise e
