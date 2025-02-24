from shared.src.enums import LanguageEnum
from shared.src.tables.links.link_resources_table import LinkResourceTable, LinkResourceTranslationTable, LinkType


link_resource_constants = [
    LinkResourceTable(
        id="MOODLE",
        url="https://moodle.lmu.de/my/",
        types=[LinkType.INTERNAL],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US, 
                title="Moodle", 
                description="Courses and learning materials", 
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN, 
                title="Moodle", 
                description="Kurse und Lernmaterialien", 
            )
        ]
    ),
    LinkResourceTable(
        id="LSF",
        url="https://lsf.verwaltung.uni-muenchen.de/",
        types=[LinkType.INTERNAL],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US, 
                title="LSF", 
                description="Course Management System", 
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN, 
                title="LSF", 
                description="Veranstaltungs-Management-System", 
            )
        ]
    ),
    LinkResourceTable(
        id="ANNY",
        url="https://auth.anny.eu/start-session?entityId=https://lmuidp.lrz.de/idp/shibboleth",
        types=[LinkType.EXTERNAL],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US, 
                title="Anny", 
                description="App for booking seats and rooms in libraries", 
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN, 
                title="Anny", 
                description="App für das Buchen von Sitzplätzen und Räumen in Bibliotheken", 
            )
        ]
    )
]