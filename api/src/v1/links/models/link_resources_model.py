from typing import List

from pydantic import BaseModel, RootModel

from shared.src.tables.links import LinkResourceTable, LinkResourceTranslationTable


class LinkResource(BaseModel):
    title: str
    description: str
    url: str
    favicon_url: str | None = None
    types: List[str] = []
    aliases: List[str] = []
    
    @classmethod
    def from_table(cls, link: LinkResourceTable):
        translations: LinkResourceTranslationTable = link.translations[0] if link.translations else None
        title = translations.title if translations else "not translated"
        description = translations.description if translations else "not translated"
        aliases = translations.aliases if translations else []
        
        return cls(
            url=link.url,
            favicon_url=link.favicon_url,
            types=link.types,
            title=title,
            description=description,
            aliases=aliases
        )
        
class LinkResources(RootModel):
    root: List[LinkResource]
    
    @classmethod
    def from_table(cls, links: List[LinkResourceTable]):
        return cls([LinkResource.from_table(link) for link in links])

