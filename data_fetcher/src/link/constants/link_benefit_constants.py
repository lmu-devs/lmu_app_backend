from shared.src.enums import LanguageEnum
from shared.src.tables.link import LinkBenefitTable, LinkBenefitTranslationTable

link_benefit_constants = [
    LinkBenefitTable(
        id="MVG",
        url="https://www.mvg.de/abos-tickets/abos/ermaessigungsticket.html",
        image_url="https://www.mvg.de/dam/jcr:86494fae-6133-41bc-ac01-ac8e4ab95c10/19268-MVG-29E-Ticket-Student-Headerbild-Landingpage-1920x1080_E01.jpg",
        translations=[
            LinkBenefitTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="MVG Ermäßigungsticket",
                description="Discounted ticket for 38€ per month",
            ),
            LinkBenefitTranslationTable(
                language=LanguageEnum.GERMAN,
                title="MVG Ermäßigungsticket",
                description="Vergünstigtes Deutschlandticket für 38€ pro Monat",
            ),
        ],
    ),
    LinkBenefitTable(
        id="NEWS",
        url="https://emedien.ub.uni-muenchen.de/login?url=https://www.pressreader.com/",
        translations=[
            LinkBenefitTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="News and Magazines",
                description="Free and current",
            ),
            LinkBenefitTranslationTable(
                language=LanguageEnum.GERMAN,
                title="News and Zeitschriften",
                description="Kostenlose und tagesaktuell",
            ),
        ],
    ),
    LinkBenefitTable(
        id="PHILHARMONIKER",
        url="https://www.mphil.de/",
        image_url="https://www.mphil.de/fileadmin/_processed_/b/1/csm_Muenchner_Philharmoniker_credit_Tobias_Hase_4_84f85ba94a.jpg.webp",
        translations=[
            LinkBenefitTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Munich Philharmoniker",
                description="Discounted tickets for students",
            ),
            LinkBenefitTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Münchner Philharmoniker",
                description="Ermäßigte Tickets für Studenten",
            ),
        ],
    ),
    LinkBenefitTable(
        id="STAATSOPER",
        url="https://www.staatsoper.de/",
        image_url="https://www.staatsoper.de/media/_processed_/9/8/csm_Stufenbar_20-08-2020_052_37d06a9c1f.png",
        translations=[
            LinkBenefitTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Staatsoper",
                description="Discounted tickets for students",
            ),
            LinkBenefitTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Staatsoper",
                description="Ermäßigte Tickets für Studenten",
            ),
        ],
    ),
    LinkBenefitTable(
        id="GEATNERPLATZTHEATER",
        url="https://www.gaertnerplatztheater.de/de/seiten/angebote-fuer-studierende.html",
        image_url="https://www.gaertnerplatztheater.de/uploads/Foto_Video_Galerien/galerien/Haus/Theater_au%C3%9Fen/_10a9640-regpogozach.jpg?1780_750",
        translations=[
            LinkBenefitTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="Gärtnerplatz Theater",
                description="Discounted tickets for students",
            ),
            LinkBenefitTranslationTable(
                language=LanguageEnum.GERMAN,
                title="Gärtnerplatz Theater",
                description="Ermäßigte Tickets für Studenten",
            ),
        ],
    ),
    LinkBenefitTable(
        id="GITHUB_EDUCATION",
        url="https://github.com/education",
        image_url="https://education.github.com/assets/pack/opengraph-image-c6d692948bb5fbf237b8a72d6576b4dcc84586335b522a6036904fc16ec7eccd.png",
        translations=[
            LinkBenefitTranslationTable(
                language=LanguageEnum.ENGLISH_US,
                title="GitHub Education",
                description="Free GitHub Pro, GitHub Copilot, GitHub Codespaces, GitHub Student Developer Pack",
            ),
            LinkBenefitTranslationTable(
                language=LanguageEnum.GERMAN,
                title="GitHub Education",
                description="Kostenloses GitHub Pro, GitHub Copilot, GitHub Codespaces, GitHub Student Developer Pack",
            ),
        ],
    ),
]
