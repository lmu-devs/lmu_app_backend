from shared.src.tables.links.links_table import LinkTable, LinkTranslationTable, LinkType
from shared.src.enums import LanguageEnum

link_constants = [
    LinkTable(
        id="MOODLE",
        url="https://moodle.lmu.de/my/",
        types=[LinkType.INTERNAL],
        translations=[
            LinkTranslationTable(
                language=LanguageEnum.ENGLISH_US, 
                title="Moodle", 
                description="Courses and learning materials", 
            ),
            LinkTranslationTable(
                language=LanguageEnum.GERMAN, 
                title="Moodle", 
                description="Kurse und Lernmaterialien", 
            )
        ]
    ),
    LinkTable(
        id="LSF",
        url="https://lsf.verwaltung.uni-muenchen.de/",
        types=[LinkType.INTERNAL],
        translations=[
            LinkTranslationTable(
                language=LanguageEnum.ENGLISH_US, 
                title="LSF", 
                description="Course Management System", 
            ),
            LinkTranslationTable(
                language=LanguageEnum.GERMAN, 
                title="LSF", 
                description="Veranstaltungs-Management-System", 
            )
        ]
    ),
    LinkTable(
        id="ANNY",
        url="https://auth.anny.eu/start-session?entityId=https://lmuidp.lrz.de/idp/shibboleth",
        types=[LinkType.EXTERNAL],
        translations=[
            LinkTranslationTable(
                language=LanguageEnum.ENGLISH_US, 
                title="Anny", 
                description="App for booking seats and rooms in libraries", 
            ),
            LinkTranslationTable(
                language=LanguageEnum.GERMAN, 
                title="Anny", 
                description="App für das Buchen von Sitzplätzen und Räumen in Bibliotheken", 
            )
        ]
    )
]