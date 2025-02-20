from typing import List

from pydantic import BaseModel, RootModel

from shared.src.tables.links.links_table import LinkTable


class Link(BaseModel):
    title: str
    description: str
    url: str
    favicon_url: str | None = None
    tags: List[str]
    aliases: List[str] | None = None
    
    @classmethod
    def from_table(cls, link: LinkTable):
        title = link.translations[0].title if link.translations else "not translated"
        description = link.translations[0].description if link.translations else "not translated"
        aliases = link.translations[0].aliases if link.translations else []
        
        return cls(
            url=link.url,
            favicon_url=link.favicon_url,
            tags=link.types,
            title=title,
            description=description,
            aliases=aliases
        )
        
class Links(RootModel):
    root: List[Link]
    
    @classmethod
    def from_table(cls, links: List[LinkTable]):
        return cls([Link.from_table(link) for link in links])

