import uuid
from pathlib import Path
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v2.core.flatten_response_util import flatten_response
from api.src.v2.core.service.like_service import LikeService
from api.src.v2.core.transform_images_response_utils import transform_images_response
from shared.src.core.settings import get_settings
from shared.src.enums.language_enums import LanguageEnum
from shared.src.models.rating_model import Rating
from shared.src.services.directus_service import DirectusService
from shared.src.tables import WishlistLikeTable

from ..models.wishlist_model import Wishlist, Wishlists


class WishlistService:
    def __init__(self, db: AsyncSession = None, language: LanguageEnum = LanguageEnum.GERMAN):
        self.db = db
        self.language = language
        self.settings = get_settings()
        self.directus = DirectusService()
        self.like_service = LikeService(db) if db else None

    async def get_wishlists(
        self,
        language: LanguageEnum = LanguageEnum.GERMAN,
        wishlist_id: Optional[int] = None,
        user_id: Optional[uuid.UUID] = None,
    ) -> Wishlists:
        try:
            query_path = Path(__file__).parent.parent / "graphql" / "get_wishlist_query.graphql"
            response = self.directus.execute_query_file(
                query_file_path=query_path,
                variables={"languageCode": language.value},
            )

            flattened_response = flatten_response(response)
            flattened_response = transform_images_response(flattened_response)
            wishlists = flattened_response["wishlists"]

            # Filter by ID if specified
            if wishlist_id:
                wishlists = [w for w in wishlists if int(w["id"]) == wishlist_id]
                if not wishlists:
                    return Wishlists(root=[])

            # Add rating information
            # Get like counts for all wishlists
            like_counts = await self.like_service.get_like_counts(WishlistLikeTable, [int(w["id"]) for w in wishlists])

            # Add user's like status if a user is provided
            liked_wishlist_ids = []
            if user_id:
                liked_wishlist_ids = await self.like_service.get_user_likes(WishlistLikeTable, user_id)

            # Add rating information to each wishlist
            for wishlist in wishlists:
                wishlist_id_int = int(wishlist["id"])
                like_count = like_counts.get(wishlist_id_int, 0)
                is_liked = wishlist_id_int in liked_wishlist_ids if user_id else None

                wishlist["rating"] = Rating.from_params(like_count=like_count, is_liked=is_liked)

            # Validate and convert to Pydantic model
            validated_wishlists = [Wishlist(**wishlist) for wishlist in wishlists]
            return Wishlists(root=validated_wishlists)
        except Exception as e:
            raise e

    async def toggle_like(self, wishlist_id: int, user_id: uuid.UUID) -> bool:
        """Toggle like status for a wishlist"""
        if not self.db:
            raise ValueError("Database connection required for like operations")

        return await self.like_service.toggle_like(WishlistLikeTable, wishlist_id, user_id)
