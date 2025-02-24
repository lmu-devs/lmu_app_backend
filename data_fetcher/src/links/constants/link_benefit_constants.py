from shared.src.enums import LanguageEnum
from shared.src.tables.links import LinkBenefitTable, LinkBenefitTranslationTable


link_benefit_constants = [
    LinkBenefitTable(
        id="MVG",
        url="https://www.mvg.de/abos-tickets/abos/ermaessigungsticket.html",
        image_url="https://www.mvg.de/dam/jcr:86494fae-6133-41bc-ac01-ac8e4ab95c10/19268-MVG-29E-Ticket-Student-Headerbild-Landingpage-1920x1080_E01.jpg",
        translations=[
            LinkBenefitTranslationTable(
                language=LanguageEnum.ENGLISH_US, 
                title="MVG Ermäßigungsticket", 
                description="Discounted ticket for 38€ per month newspapers and magazines free and daily current Münchner Philharmoniker Discounted tickets for students Staatsoper Cheap tickets and numerous activities", 
            ),
            LinkBenefitTranslationTable(
                language=LanguageEnum.GERMAN, 
                title="MVG Ermäßigungsticket", 
                description="Vergünstigtes Deutschlandticket für 38€ pro Monat Zeitung und Zeitschriften Kostenlos und tagesaktuell Münchner Philharmoniker Ermäßigte Tickets für Studenten Staatsoper Günstigere Tickets und zahlreiche Aktivitäten", 
            )
        ]
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
            )
        ]
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
            )
        ]
    ),
    LinkBenefitTable(
        id="STAATSOPER",
        url="https://www.staatsoper.de/de/kontakt/kontaktformular/",
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
            )
        ]
    )
]