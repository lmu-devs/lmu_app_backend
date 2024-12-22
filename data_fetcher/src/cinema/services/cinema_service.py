from shared.src.enums import LanguageEnum, UniversityEnum
from shared.src.tables import CinemaLocationTable, CinemaTable, CinemaTranslationTable
from shared.src.core.logging import get_cinema_fetcher_logger

from ..constants.url_constants import LMU_CINEMA_URL, TUM_CINEMA_URL, HM_CINEMA_URL
from ..constants.location_constants import CinemaLocationConstants

logger = get_cinema_fetcher_logger(__name__)

class CinemaService:
    
    def get_all_cinema_tables(self) -> list[CinemaTable]:
        
        cinemas = []
        
        cinemas.append(self.lmu_cinemas())
        cinemas.append(self.tum_cinemas())
        cinemas.append(self.hm_cinemas())
        
        logger.info(f"Successfully created {len(cinemas)} cinemas")
        return cinemas
    
    lmu_cinema_id = UniversityEnum.LMU.value
    tum_cinema_id = UniversityEnum.TUM.value
    hm_cinema_id = UniversityEnum.HM.value
    
    lmu_translations = [
        CinemaTranslationTable(
            cinema_id=lmu_cinema_id,
            language=LanguageEnum.GERMAN.value,
            title="LMU Kino",
            description=[
                {
                    "emoji": "🍿",
                    "description": "Eigene Snacks erlaubt"
                },
                {
                    "emoji": "🎟️",
                    "description": "Keine Vorverkauf- und Reservierungsmöglichkeit"
                },
                {
                    "emoji": "☁️",
                    "description": "Erste Besucher erhalten ein Kissen"
                }
            ],
        ),
        CinemaTranslationTable(
            cinema_id=lmu_cinema_id,
            language=LanguageEnum.ENGLISH_US.value,
            title="LMU Cinema",
            description=[
                {
                    "emoji": "🍿",
                    "description": "Bring you own snacks"
                },
                {
                    "emoji": "🎟️",
                    "description": "No presale, and reservation"
                },
                {
                    "emoji": "☁️",
                    "description": "Free pillow for first visitors"
                }
            ],
        )
    ]
    
    tum_translations = [
        CinemaTranslationTable(
            cinema_id=tum_cinema_id,
            language=LanguageEnum.GERMAN.value,
            title="TUM Kino",
            description=[
                {
                    "emoji": "🎥",
                    "description": "Test"
                },
                {
                    "emoji": "🎥",
                    "description": "Test2"
                }
            ],
        ),
        CinemaTranslationTable(
            cinema_id=tum_cinema_id,
            language=LanguageEnum.ENGLISH_US.value,
            title="TUM Cinema",
            description=[
                {
                    "emoji": "🎥",
                    "description": "Test"
                },
                {
                    "emoji": "🎥",
                    "description": "Test2"
                }
            ],
        )
    ]
    
    hm_translations = [
        CinemaTranslationTable(
            cinema_id=hm_cinema_id,
            language=LanguageEnum.GERMAN.value,
            title="HM Kino",
            description=[
                {
                    "emoji": "🎥",
                    "description": "Test"
                },
                {
                    "emoji": "🎥",
                    "description": "Test2"
                }
            ],
        ),
        CinemaTranslationTable(
            cinema_id=hm_cinema_id,
            language=LanguageEnum.ENGLISH_US.value,
            title="HM Cinema",
            description=[
                {
                    "emoji": "🎥",
                    "description": "Test"
                },
                {
                    "emoji": "🎥",
                    "description": "Test2"
                }
            ],
        )
    ]
    
    def lmu_cinemas(self) -> CinemaTable:
        return CinemaTable( 
            id=self.lmu_cinema_id,
            external_link=LMU_CINEMA_URL,
            instagram_link="https://www.instagram.com/das.ukino/",
            location=CinemaLocationTable(**vars(CinemaLocationConstants[UniversityEnum.LMU])),
            translations=self.lmu_translations
        )
        
    def tum_cinemas(self) -> CinemaTable:
        return CinemaTable(
            id=self.tum_cinema_id,
            external_link=TUM_CINEMA_URL,
            instagram_link="https://www.instagram.com/dertufilm/",
            translations=self.tum_translations
        )
        
    def hm_cinemas(self) -> CinemaTable:
        return CinemaTable(
            id=self.hm_cinema_id,
            external_link=HM_CINEMA_URL,
            instagram_link="https://www.instagram.com/hm__kino/",
            location=CinemaLocationTable(**vars(CinemaLocationConstants[UniversityEnum.HM])),
            translations=self.hm_translations
        )
    
    
    
    
    