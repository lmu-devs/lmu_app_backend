from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from api.src.v1.core.translation_utils import apply_translation_query
from shared.src.enums.language_enums import LanguageEnum
from shared.src.tables.link.link_resources_table import LinkResourceTable, LinkResourceTranslationTable


class LinkResourceService:
    def __init__(self, db: AsyncSession, language: LanguageEnum = LanguageEnum.GERMAN):
        self.db = db
        self.language = language 
        
    async def get_links(self):
        stmt = select(LinkResourceTable)
        stmt = apply_translation_query(base_query=stmt, model=LinkResourceTable, translation_model=LinkResourceTranslationTable, language=self.language)
        result = await self.db.execute(stmt)
        links = result.scalars().unique().all()
        return links
