from pathlib import Path
from typing import List

from api.src.v1.core.flatten_response_util import flatten_response
from api.src.v2.core.transform_images_response_utils import transform_images_response
from api.src.v2.core.utils.directus_mappers import map_directus_location
from shared.src.core.settings import get_settings
from shared.src.enums.language_enums import LanguageEnum
from shared.src.services.directus_service import DirectusService

from ..models.club_model import Club, ClubCategory, ClubsResponse


class ClubService:
    def __init__(self):
        self.settings = get_settings()
        self.directus = DirectusService()

    async def get_clubs(
        self,
        language: LanguageEnum = LanguageEnum.GERMAN,
    ) -> ClubsResponse:
        try:
            query_path = Path(__file__).parent.parent / "graphql" / "club_query.graphql"
            response = self.directus.execute_query_file(
                query_file_path=query_path,
                variables={"languageCode": language.value},
            )

            transformed_response = transform_images_response(response)
            flattened_response = flatten_response(transformed_response)

            raw_categories = flattened_response.get("student_club_categories", [])
            raw_clubs = flattened_response.get("student_clubs", [])

            category_to_club_ids = {cat.get("id"): [] for cat in raw_categories}
            
            clubs = []
            for club in raw_clubs:
                universities = club.pop("univerities", None)
                if isinstance(universities, list) and universities:
                    club["university_id"] = universities[0].get("id")
                elif isinstance(universities, dict):
                    club["university_id"] = universities.get("id")

                address = club.pop("address", None)
                raw_location = club.pop("location", None)
                club["location"] = map_directus_location(address, raw_location)

                category_data = club.pop("category", None)
                category_id = None
                if isinstance(category_data, dict):
                    category_id = category_data.get("id")
                elif isinstance(category_data, str):
                    category_id = category_data
                
                if category_id and category_id in category_to_club_ids:
                    category_to_club_ids[category_id].append(club["id"])

                clubs.append(Club(**club))

            categories = []
            for cat in raw_categories:
                cat_id = cat.get("id")
                club_ids_for_cat = category_to_club_ids.get(cat_id, [])
                
                if len(club_ids_for_cat) > 0:
                    categories.append(
                        ClubCategory(
                            id=cat_id,
                            title=cat.get("title", ""), 
                            emoji=cat.get("emoji", ""),
                            club_ids=club_ids_for_cat
                        )
                    )

            return ClubsResponse(
                club_categories=categories,
                clubs=clubs
            )

        except Exception as e:
            raise e