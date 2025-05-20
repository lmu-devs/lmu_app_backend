from pathlib import Path

from api.src.v2.core.flatten_response_util import flatten_response
from api.src.v2.core.transform_images_response_utils import transform_images_response
from api.src.v2.link.models.link_benefits_model import LinkBenefitResponse
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

            transformed_response = transform_images_response(response)
            flattened_response = flatten_response(transformed_response)

            return LinkBenefitResponse(**flattened_response)
        except Exception as e:
            raise e
