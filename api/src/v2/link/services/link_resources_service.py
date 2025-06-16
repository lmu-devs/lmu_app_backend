import uuid
from pathlib import Path
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v2.core.flatten_response_util import flatten_response
from api.src.v2.core.service.like_service import LikeService
from shared.src.core.settings import get_settings
from shared.src.enums.language_enums import LanguageEnum
from shared.src.models.rating_model import Rating
from shared.src.services.directus_service import DirectusService
from shared.src.tables.link.link_resources_table import LinkResourceLikeTable

from ..models.link_resources_model import LinkResource


class LinkResourceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.like_service = LikeService(db)
        self.settings = get_settings()
        self.directus = DirectusService()

    async def get_links(
        self,
        language: LanguageEnum = LanguageEnum.GERMAN,
        user_id: Optional[uuid.UUID] = None,
    ) -> List[LinkResource]:
        try:
            # Execute GraphQL query
            query_path = Path(__file__).parent.parent / "graphql" / "link_recources_query.graphql"
            response = self.directus.execute_query_file(
                query_file_path=query_path,
                variables={"languageCode": language.value},
            )

            # Flatten the response
            flattened_response = flatten_response(response)
            links = flattened_response["links"]

            # Get like counts for all links
            like_counts = await self.like_service.get_like_counts(LinkResourceLikeTable, [link["id"] for link in links])

            # Get user's liked links if user_id is provided
            liked_link_ids = []
            if user_id:
                liked_link_ids = await self.like_service.get_user_likes(LinkResourceLikeTable, user_id)

            # Add rating information and process each link
            processed_links = []
            for link in links:
                like_count = like_counts.get(link["id"], 0)
                is_liked = link["id"] in liked_link_ids if user_id else None

                # Add rating information
                link["rating"] = Rating.from_params(like_count=like_count, is_liked=is_liked)

                # Extract faculty IDs from nested faculties_id structure
                link["faculties"] = [
                    faculty["faculties_id"]["id"]
                    for faculty in link.get("faculties", [])
                    if faculty.get("faculties_id")
                ]

                # Create validated link object
                processed_links.append(LinkResource(**link))

            # Return the complete response
            return processed_links

        except Exception as e:
            raise e

    async def toggle_like(self, id: str, user_id: str):
        return await self.like_service.toggle_like(LinkResourceLikeTable, id, user_id)
