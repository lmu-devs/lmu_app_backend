# from typing import List

# from pydantic import BaseModel, RootModel

# from shared.src.tables.links.benefits_table import BenefitTable, BenefitTranslationTable


# class Benefit(BaseModel):
#     title: str
#     description: str
#     url: str
#     image_url: str | None = None
#     tags: List[str]
#     aliases: List[str] | None = None
    
#     @classmethod
#     def from_table(cls, benefit: BenefitTable):
#         title = benefit.translations[0].title if benefit.translations else "not translated"
#         description = benefit.translations[0].description if benefit.translations else "not translated"
#         aliases = benefit.translations[0].aliases if benefit.translations else []
        
#         return cls(
#             url=benefit.url,
#             image_url=benefit.image_url,
#             tags=benefit.types,
#             title=title,
#             description=description,
#             aliases=aliases
#         )
        
# class Benefits(RootModel):
#     root: List[Benefit]
    
#     @classmethod
#     def from_table(cls, benefits: List[BenefitTable]):
#         return cls([Benefit.from_table(benefit) for benefit in benefits])

