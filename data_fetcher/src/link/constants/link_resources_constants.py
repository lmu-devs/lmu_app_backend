from shared.src.enums import LanguageEnum
from shared.src.enums.faculty_enums import FacultyEnum
from shared.src.tables.link.link_resources_table import (
    LinkResourceTable,
    LinkResourceTranslationTable,
    LinkType,
)

link_resource_constants = [
    LinkResourceTable(
        id="MOODLE",
        url="https://moodle.lmu.de/my/",
        types=[LinkType.INTERNAL],
        faculties=[],
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
            ),
        ],
    ),
    LinkResourceTable(
        id="LSF",
        url="https://lsf.verwaltung.uni-muenchen.de/",
        types=[LinkType.INTERNAL],
        faculties=[],
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
            ),
        ],
    ),
    LinkResourceTable(
        id="ANNY",
        url="https://auth.anny.eu/start-session?entityId=https://lmuidp.lrz.de/idp/shibboleth",
        types=[LinkType.EXTERNAL],
        faculties=[],
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
            ),
        ],
    ),
    LinkResourceTable(
        id="IMMATRICULATION",
        url="https://qissos.verwaltung.uni-muenchen.de/qisserversos/",
        types=[LinkType.INTERNAL],
        faculties=[],
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
            ),
        ],
    ),
    LinkResourceTable(
        id="MAILBOX",
        url="https://webmail.lrz.de/",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="E-Mail",
                description="LMU Web Mail. Use your LRZ ID and LMU password to login. (LRZ ID is found in the User Account)",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="E-Mail",
                description="LMU Web Mail. Verwende deine LRZ ID und dein LMU Passwort um dich einzuloggen. (LRZ ID ist in deinem Benutzerkonto zu finden)",
            ),
        ],
    ),
    LinkResourceTable(
        id="USER_ACCOUNT",
        url="https://www.portal.uni-muenchen.de/benutzerkonto/#!/",
        types=[LinkType.INTERNAL],
        faculties=[],
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
            ),
        ],
    ),
    LinkResourceTable(
        id="LMU_DEVELOPERS",
        url="https://lmu-dev.org",
        types=[LinkType.EXTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="LMU Developers",
                description="Student organization for developers",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="LMU Developers",
                description="Studentenorganisation für Entwickler",
            ),
        ],
    ),
    LinkResourceTable(
        id="EXCHANGE",
        url="https://www.lmu.de/de/workspace-fuer-studierende/auslandserfahrung-sammeln/auslandsstudium/lmuexchange/index.html",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="LMU Exchange",
                description="Exchange program for students",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="LMU Exchange",
                description="Austauschprogramm für Studierende",
            ),
        ],
    ),
    LinkResourceTable(
        id="PRINT",
        url="https://upload.printservice.uni-muenchen.de/RicohmyPrint/Login.aspx",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Print Service",
                description="You should read the instructions before using the service.",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Print Service",
                description="Druckdienst. Kleiner Tipp: Lese die Hinweise vor dem Drucken.",
            ),
        ],
    ),
    LinkResourceTable(
        id="LIBRARY",
        url="https://www.ub.uni-muenchen.de/bibliotheken/bibs-a-bis-z/index.html",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Library",
                description="List of libraries",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Bibliothek",
                description="Liste der Bibliotheken",
            ),
        ],
    ),
    LinkResourceTable(
        id="STUVE",
        url="https://www.stuve.uni-muenchen.de/stuve/index.html",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Student Council",
                description="Council of students",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="StuVe",
                description="Studentenvertretung der LMU",
            ),
        ],
    ),
    LinkResourceTable(
        id="M365",
        url="https://www.lmu.de/m365-login",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Microsoft 365",
                description="Office 365, OneDrive, etc. Use your LMU email and password to login.",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Microsoft 365",
                description="Office 365, OneDrive, etc. Verwende deine LMU E-Mail und dein Passwort um dich einzuloggen.",
            ),
        ],
    ),
    LinkResourceTable(
        id="SYNC_AND_SHARE",
        url="https://syncandshare.lrz.de/login",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Cloud Storage",
                description="LRZ Sync and Share",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Cloud Storage",
                description="LRZ Sync and Share",
            ),
        ],
    ),
    LinkResourceTable(
        id="NEWS_AND_EVENTS",
        url="https://www.lmu.de/de/workspace-fuer-studierende/meldungen-und-termine/",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="News and Events",
                description="Important deadlines and study matters.",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Meldungen und Termine",
                description="Wichtige Fristen und Studienangelegenheiten.",
            ),
        ],
    ),
    LinkResourceTable(
        id="GRADES_COMPUTER_SCIENCE",
        url="https://pvineu.ifi.lmu.de",
        types=[LinkType.INTERNAL],
        faculties=[FacultyEnum.MATH_INFO_STATS],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Grades CS",
                description="Grades and Transcript for Computer Science Students.",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Noten Informatik",
                description="Noten und Transkript für (Medien)-Informatik & HCI Studierende",
            ),
        ],
    ),
    LinkResourceTable(
        id="BEITRAGSKONTO",
        url="https://qissos.verwaltung.uni-muenchen.de/qisserversos/",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Semester Fee",
                description="Pay your semester fee online",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Semesterbeitrag",
                description="Zahle deinen Semesterbeitrag online über das Beitragskonto",
            ),
        ],
    ),
    LinkResourceTable(
        id="INFORMATICS_GROUP_CHATS",
        url="https://linktr.ee/lmu_info",
        types=[LinkType.INTERNAL],
        faculties=[FacultyEnum.MATH_INFO_STATS],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Informatics Group Chats",
                description="WhatsApp groups for Informatics Students",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Informatik-Gruppen-Chats",
                description="WhatsApp-Gruppen für Informatik-Studierende",
            ),
        ],
    ),
]
