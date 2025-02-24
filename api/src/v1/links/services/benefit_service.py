# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession

# from api.src.v1.core.translation_utils import apply_translation_query
# from shared.src.enums.language_enums import LanguageEnum
# from shared.src.tables.links.benefits_table import BenefitTable, BenefitTranslationTable


# class BenefitService:
#     def __init__(self, db: AsyncSession, language: LanguageEnum = LanguageEnum.GERMAN):
#         self.db = db
#         self.language = language 
    
#     async def get_benefits(self):
#         stmt = select(BenefitTable)
#         stmt = apply_translation_query(base_query=stmt, model=BenefitTable, translation_model=BenefitTranslationTable, language=self.language)
#         result = await self.db.execute(stmt)
#         benefits = result.scalars().unique().all()
#         return benefits
