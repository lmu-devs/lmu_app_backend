from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.src.v1.core.service.like_service import LikeService
from api.src.v1.core.translation_utils import apply_translation_query
from shared.src.enums.language_enums import LanguageEnum
from shared.src.tables.link.link_resources_table import (
    LinkResourceLikeTable,
    LinkResourceTable,
    LinkResourceTranslationTable,
)


class LinkResourceService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.like_service = LikeService(db)

    async def get_links(self, language: LanguageEnum = LanguageEnum.GERMAN, user_id: str | None = None):
        stmt = select(LinkResourceTable)
        stmt = apply_translation_query(
            base_query=stmt,
            model=LinkResourceTable,
            translation_model=LinkResourceTranslationTable,
            language=language,
        )

        # Load likes relationship for counting
        stmt = stmt.options(
            selectinload(LinkResourceTable.likes),
        )

        result = await self.db.execute(stmt)
        links = result.scalars().unique().all()

        # Add is_liked property if user_id is provided
        if user_id:
            liked_ids = await self.like_service.get_user_likes(LinkResourceLikeTable, user_id)
            for link in links:
                link.is_liked = link.id in liked_ids

        return links

    async def toggle_like(self, id: str, user_id: str):
        return await self.like_service.toggle_like(LinkResourceLikeTable, id, user_id)
