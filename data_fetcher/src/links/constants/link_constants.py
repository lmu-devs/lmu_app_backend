from shared.src.tables.links.links_table import LinkTable, LinkTranslationTable, LinkType
from shared.src.enums import LanguageEnum

link_constants = [
    LinkTable(
        id="papa",
        url="https://www.google.com",
        favicon_url="https://www.google.com/favicon.ico",
        types=[LinkType.EXTERNAL],
        translations=[
            LinkTranslationTable(
                language=LanguageEnum.ENGLISH_US, 
                title="Google", 
                description="Search the web", 
            ),
            LinkTranslationTable(
                language=LanguageEnum.GERMAN, 
                title="Google", 
                description="Suchen Sie das Web", 
            )
        ]
    )
]