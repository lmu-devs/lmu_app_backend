from typing import List

from pydantic import BaseModel, RootModel

from shared.src.tables.link import LinkBenefitTable, LinkBenefitTranslationTable


class LinkBenefit(BaseModel):
    title: str
    description: str
    url: str
    favicon_url: str | None = None
    image_url: str | None = None
    aliases: List[str] = []

    @classmethod
    def from_table(cls, benefit: LinkBenefitTable):
        translations: LinkBenefitTranslationTable = (
            benefit.translations[0] if benefit.translations else None
        )
        title = translations.title if translations else "not translated"
        description = translations.description if translations else "not translated"
        aliases = translations.aliases if translations and translations.aliases else []

        return cls(
            url=benefit.url,
            favicon_url=benefit.favicon_url,
            image_url=benefit.image_url,
            title=title,
            description=description,
            aliases=aliases,
        )


class LinkBenefits(RootModel):
    root: List[LinkBenefit]

    @classmethod
    def from_table(cls, benefits: List[LinkBenefitTable]):
        return cls([LinkBenefit.from_table(benefit) for benefit in benefits])
