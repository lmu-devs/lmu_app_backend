from typing import List

from pydantic import BaseModel, RootModel

from shared.src.tables.links import LinkBenefitTable, LinkBenefitTranslationTable


class Benefit(BaseModel):
    title: str
    description: str
    url: str
    image_url: str | None = None
    aliases: List[str] = []
    
    @classmethod
    def from_table(cls, benefit: LinkBenefitTable):
        translations: LinkBenefitTranslationTable = benefit.translations[0] if benefit.translations else None
        title = translations.title if translations else "not translated"
        description = translations.description if translations else "not translated"
        aliases = translations.aliases if translations else []
        
        return cls(
            url=benefit.url,
            image_url=benefit.image_url,
            title=title,
            description=description,
            aliases=aliases
        )
        
class LinkBenefits(RootModel):
    root: List[Benefit]
    
    @classmethod
    def from_table(cls, benefits: List[LinkBenefitTable]):
        return cls([Benefit.from_table(benefit) for benefit in benefits])

