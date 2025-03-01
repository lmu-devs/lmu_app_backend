from shared.src.enums import LanguageEnum
from shared.src.tables.link.link_resources_table import LinkResourceTable, LinkResourceTranslationTable, LinkType


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
    ),
    LinkResourceTable(
        id="IMMATRICULATION",
        url="https://qissos.verwaltung.uni-muenchen.de/qisserversos/",
        types=[LinkType.INTERNAL],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US, 
                title="Study Administration", 
                description="Immatriculation, Study Certificate, etc.", 
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN, 
                title="Verwaltung Studium", 
                description="Immatrikulation, Studienbescheinigung, Beitragskonto, etc.", 
            )
        ]
    ),
    LinkResourceTable(
        id="MAILBOX",
        url="https://mailbox.portal.uni-muenchen.de/webmail/webmail/ui/MainPage.html",
        types=[LinkType.INTERNAL],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US, 
                title="E-Mail", 
                description="Online LMU Mail Portal", 
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN, 
                title="E-Mail", 
                description="Online LMU Mail Portal", 
            )
        ]
    ),
    LinkResourceTable(
        id="USER_ACCOUNT",
        url="https://www.portal.uni-muenchen.de/benutzerkonto/#!/",
        types=[LinkType.INTERNAL],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US, 
                title="User Account", 
                description="LMU Card, E-Mail, LRZ ID, etc.", 
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN, 
                title="Benutzerkonto", 
                description="LMU Karte, E-Mail, LRZ ID, etc.", 
            )
        ]
    )
]