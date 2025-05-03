from typing import List

from pydantic import BaseModel, RootModel

from shared.src.enums.faculty_enums import FacultyEnum
from shared.src.models.rating_model import Rating
from shared.src.tables.link import (
    LinkResourceTable,
    LinkResourceTranslationTable,
    LinkType,
)


class LinkResource(BaseModel):
    id: str
    title: str
    description: str
    url: str
    favicon_url: str | None = None
    faculties: List[FacultyEnum] = []
    types: List[LinkType] = []
    aliases: List[str] = []
    rating: Rating

    @classmethod
    def from_table(cls, link: LinkResourceTable):
        translations: LinkResourceTranslationTable = link.translations[0] if link.translations else None
        title = translations.title if translations else "not translated"
        description = translations.description if translations else "not translated"
        aliases = translations.aliases if translations and translations.aliases else []
        rating = Rating(like_count=link.like_count, is_liked=link.is_liked)

        return cls(
            id=link.id,
            url=link.url,
            favicon_url=link.favicon_url,
            types=link.types,
            faculties=link.faculties,
            title=title,
            description=description,
            aliases=aliases,
            rating=rating,
        )


class LinkResources(RootModel):
    root: List[LinkResource]

    @classmethod
    def from_table(cls, links: List[LinkResourceTable]):
        return cls([LinkResource.from_table(link) for link in links])
