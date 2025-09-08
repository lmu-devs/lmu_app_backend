from pathlib import Path

from api.src.v2.benefit.models.benefits_model import BenefitResponse
from api.src.v2.core.flatten_response_util import flatten_response
from api.src.v2.core.transform_images_response_utils import transform_images_response
from shared.src.core.settings import get_settings
from shared.src.enums.language_enums import LanguageEnum
from shared.src.services.directus_service import DirectusService


class BenefitService:
    def __init__(self, language: LanguageEnum = LanguageEnum.GERMAN):
        self.language = language
        self.settings = get_settings()
        self.directus = DirectusService()

    async def get_benefits(self):
        try:
            query_path = Path(__file__).parent.parent / "graphql" / "benefits_query.graphql"
            response = self.directus.execute_query_file(
                query_file_path=query_path,
                variables={"languageCode": self.language.value},
            )

            transformed_response = transform_images_response(response)
            flattened_response = flatten_response(transformed_response)

            # Transform benefit_ids from the GraphQL response structure and filter empty types
            benefit_types_with_benefits = []
            for benefit_type in flattened_response["benefit_types"]:
                benefit_ids = [
                    benefit["benefits_id"]["id"]
                    for benefit in benefit_type.pop("benefits", [])
                    if benefit.get("benefits_id")
                ]
                if benefit_ids:  # Only include types that have benefits
                    benefit_type["benefit_ids"] = benefit_ids
                    benefit_types_with_benefits.append(benefit_type)

            flattened_response["benefit_types"] = benefit_types_with_benefits

            return BenefitResponse(**flattened_response)
        except Exception as e:
            raise e
