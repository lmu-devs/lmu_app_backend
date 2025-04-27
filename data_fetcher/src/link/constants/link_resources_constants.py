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
        types=[LinkType.EXTERNAL],
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
    LinkResourceTable(
        id="INFORMATICS_EXAM_DATES",
        url="https://studiengangskoordination.ifi.lmu.de/misc/klausuren.html",
        types=[LinkType.INTERNAL],
        faculties=[FacultyEnum.MATH_INFO_STATS],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Exam Dates",
                description="Exam dates for Computer Science, Media Informatics, Bioinformatics and HCI Students",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Klausurtermine",
                description="Klausurtermine für (Medien/Bio-)Informatik- und HCI-Studierende",
            ),
        ],
    ),
    LinkResourceTable(
        id="UNI_RADIO",
        url="http://www.m945.de/",
        types=[LinkType.EXTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Uni Radio",
                description="Daily Shows, Music, News, etc.",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Uni Radio",
                description="Daily Shows, Musik, Nachrichten, etc.",
            ),
        ],
    ),
    LinkResourceTable(
        id="CAREER_SERVICE",
        url="https://www.lmu.de/de/workspace-fuer-studierende/career-service/index.html",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Career Service",
                description="Career Service, Auslandspraktikum, Jobbörse, Karriere-Events",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Karriere Service",
                description="Karriere, Auslandspraktikum, Jobbörse, Karriere-Events",
            ),
        ],
    ),
    LinkResourceTable(
        id="STELLENPORTAL",
        url="https://www.lmu.de/de/die-lmu/arbeiten-an-der-lmu/stellenportal/index.html",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Job Portal",
                description="Work at the University",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Stellenportal",
                description="Arbeiten an der Universität",
            ),
        ],
    ),
    LinkResourceTable(
        id="INTERNATIONAL_AFFAIRS",
        url="https://www.lmu.de/en/study/important-contacts/international-office/index.html",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="International Affairs",
                description="International Affairs, Exchange Programs, etc.",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Internationale Angelegenheiten",
                description="Auslandssemester, Erasmus, LMUexchange",
            ),
        ],
    ),
    LinkResourceTable(
        id="CENTRAL_STUDY_ADVICE",
        url="https://www.lmu.de/de/studium/wichtige-kontakte/zentrale-studienberatung/index.html",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Central Study Advice",
                description="Questions about studying at LMU",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Zentrale Studienberatung",
                description="Fragen rund um das Studium",
            ),
        ],
    ),
    LinkResourceTable(
        id="CAMPUS_NEWSPAPER",
        url="https://cazelmu.wordpress.com/",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Campus Newspaper",
                description="Articles, University Life, etc.",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Campuszeitung",
                description="Artikel, Uni-Leben, etc.",
            ),
        ],
    ),
    LinkResourceTable(
        id="COUNSELING_OFFERS",
        url="https://www.lmu.de/de/die-lmu/arbeiten-an-der-lmu/zusaetzliche-angebote/diversity/wecare-lmu-2024/beratungsangebote/",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Counseling Offers",
                description="Psychological Counseling, Counseling Centers, etc.",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Beratungsangebote",
                description="Psychologische Beratung, Anlauf- und Beratungsstellen",
            ),
        ],
    ),
    LinkResourceTable(
        id="STUDYDRIVE",
        url="https://www.studydrive.net/",
        types=[LinkType.EXTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="StudyDrive",
                description="Study materials from other students",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="StudyDrive",
                description="Lernmaterialien von anderen Studierenden",
            ),
        ],
    ),
    LinkResourceTable(
        id="STUDOCU",
        url="https://www.studocu.com/de",
        types=[LinkType.EXTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Studocu",
                description="Study materials from other students",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Studocu",
                description="Lernmaterialien, Zusammenfassungen",
            ),
        ],
    ),
    LinkResourceTable(
        id="STUDENT_HOUSING",
        url="https://www.studierendenwerk-muenchen-oberbayern.de/wohnen/",
        types=[LinkType.EXTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Student Housing",
                description="Accommodation, Application",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Studentisches Wohnen",
                description="Studentenwohnheime, Bewerbung, Wohnen",
            ),
        ],
    ),
    LinkResourceTable(
        id="BAFOEG",
        url="https://stadt.muenchen.de/service/info/bafoeg-antrag-ausbildungsfoerderung/1074970/n0/",
        types=[LinkType.EXTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="BAföG",
                description="Study Funding",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="BAföG",
                description="Studiumsfinanzierung",
            ),
        ],
    ),
    LinkResourceTable(
        id="MECUM",
        url="https://www.lmu.de/de/die-lmu/struktur/zentrale-universitaetsverwaltung/informations-und-kommunikationstechnik-dezernat-vi/it-servicedesk/zentrale-it-angebote/mecum-online/",
        types=[LinkType.EXTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="MeCum",
                description="Web offers for medicine studies",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="MeCum",
                description="Web-Angebote Medizin Studium",
            ),
        ],
    ),
    LinkResourceTable(
        id="LMU_SHOP",
        url="https://lmu-shop.de/",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="LMU Shop",
                description="Merchandise",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="LMU Shop",
                description="Merchandise",
            ),
        ],
    ),
    LinkResourceTable(
        id="UNI_KULT",
        url="https://www.unikult.lmu.de/",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="UniKult e.V.",
                description="Events, Summer Festival, Ersti-Party",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="UniKult e.V.",
                description="Uni-Events, Sommerfest, Ersti-Party",
            ),
        ],
    ),
    LinkResourceTable(
        id="CDTM",
        url="https://www.cdtm.de/",
        types=[LinkType.EXTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="CDTM",
                description="Center for Digital Technology and Management",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="CDTM",
                description="Center for Digital Technology and Management",
            ),
        ],
    ),
    LinkResourceTable(
        id="STIPENDIEN",
        url="https://www.lmu.de/en/workspace-for-students/student-support-services/finance-your-studies/scholarships/",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Scholarships",
                description="Scholarships and financial aid",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Stipendien",
                description="Stipendien und Finanzhilfe",
            ),
        ],
    ),
    LinkResourceTable(
        id="BUNDESVERBAND_DEUTSCHER_STIFTUNGEN",
        url="https://www.stiftungen.org/startseite.html",
        types=[LinkType.EXTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="German Foundation Association",
                description="Financial Aid, Scholarships, etc.",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Bundesverband Deutscher Stiftungen",
                description="Finanzierung, Stiftungen, Verbände",
            ),
        ],
    ),
    LinkResourceTable(
        id="IT_SERVICEDESK",
        url="https://www.lmu.de/de/die-lmu/struktur/zentrale-universitaetsverwaltung/informations-und-kommunikationstechnik-dezernat-vi/it-servicedesk/index.html",
        types=[LinkType.INTERNAL],
        faculties=[],
        translations=[
            LinkResourceTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="IT-Servicedesk",
                description="IT-Support",
            ),
            LinkResourceTranslationTable(
                language=LanguageEnum.GERMAN,
                title="IT-Servicedesk",
                description="IT-Support",
            ),
        ],
    ),
]
