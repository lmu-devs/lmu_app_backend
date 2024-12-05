from shared.enums.language_enums import LanguageEnum
from shared.tables.cinema.cinema_table import (CinemaLocationTable,
                                               CinemaTable,
                                               CinemaTranslationTable)
from shared.enums.university_enums import UniversityEnum
from shared.core.logging import get_cinema_fetcher_logger

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
            cinema_id=lmu_cinema_id,
            language=LanguageEnum.ENGLISH_US.value,
            title="LMU Cinema",
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
            external_link="https://www.lmu.de/cinema/",
            location=CinemaLocationTable(
                address="Max-Joseph-Platz 11, 80539 München",
                latitude=48.1351,
                longitude=11.5761,
            ),
            translations=self.lmu_translations
        )
        
    def tum_cinemas(self) -> CinemaTable:
        return CinemaTable(
            id=self.tum_cinema_id,
            external_link="https://www.tum.de/cinema/",
            translations=self.tum_translations
        )
        
    def hm_cinemas(self) -> CinemaTable:
        return CinemaTable(
            id=self.hm_cinema_id,
            external_link="https://www.hm.edu/cinema/",
            location=CinemaLocationTable(
                address="Max-Joseph-Platz 11, 80539 München",
                latitude=48.1351,
                longitude=11.5761,
            ),
            translations=self.hm_translations
        )
    
    
    
    
    