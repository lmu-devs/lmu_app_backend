from pathlib import Path
from typing import List

from api.src.v1.core.flatten_response_util import flatten_response
from api.src.v2.core.transform_images_response_utils import transform_images_response
from api.src.v2.core.utils.directus_mappers import map_directus_location
from shared.src.core.settings import get_settings
from shared.src.enums.language_enums import LanguageEnum
from shared.src.services.directus_service import DirectusService

from ..models.club_model import Club


class ClubService:
    def __init__(self):
        self.settings = get_settings()
        self.directus = DirectusService()

    async def get_clubs(
        self,
        language: LanguageEnum = LanguageEnum.GERMAN,
    ) -> List[Club]:
        try:
            # Execute GraphQL query
            query_path = Path(__file__).parent.parent / "graphql" / "club_query.graphql"
            response = self.directus.execute_query_file(
                query_file_path=query_path,
                variables={"languageCode": language.value},
            )

            transformed_response = transform_images_response(response)
            flattened_response = flatten_response(transformed_response)

            clubs = []
            for club in flattened_response["student_clubs"]:
                universities = club.pop("univerities", None)
                if isinstance(universities, list) and universities:
                    club["university_id"] = universities[0].get("id")
                elif isinstance(universities, dict):
                    club["university_id"] = universities.get("id")

                address = club.pop("address", None)
                raw_location = club.pop("location", None)
                club["location"] = map_directus_location(address, raw_location)

                clubs.append(Club(**club))

            return clubs

        except Exception as e:
            raise e
