from shared.src.core.logging import get_cinema_fetcher_logger
from shared.src.core.settings import get_settings
from shared.src.enums import CinemaEnum, LanguageEnum
from shared.src.tables import CinemaImageTable, CinemaLocationTable, CinemaTable, CinemaTranslationTable

from ..constants.location_constants import CinemaLocationConstants
from ..constants.url_constants import HM_CINEMA_URL, LMU_CINEMA_URL, TUM_CINEMA_URL
from ..models.cinema_description_model import CinemaDescription


logger = get_cinema_fetcher_logger(__name__)

class CinemaService:
    def __init__(self):
        self.settings = get_settings()
        
    lmu_cinema_id = CinemaEnum.LMU.value
    hm_cinema_id = CinemaEnum.HM.value
    tum_cinema_id = CinemaEnum.TUM.value
    tum_garching_cinema_id = CinemaEnum.TUM_GARCHING.value
    
    
    def get_all_cinema_tables(self) -> list[CinemaTable]:
        
        cinemas = []
        
        cinemas.append(self.lmu_cinema())
        cinemas.append(self.hm_cinema())
        cinemas.append(self.tum_cinema())
        cinemas.append(self.tum_garching_cinema())
        
        logger.info(f"Successfully created {len(cinemas)} cinemas")
        return cinemas
    
    
    def lmu_cinema(self) -> CinemaTable:
        return CinemaTable( 
            id=self.lmu_cinema_id,
            external_link=LMU_CINEMA_URL,
            instagram_link="https://www.instagram.com/das.ukino/",
            location=CinemaLocationTable(**vars(CinemaLocationConstants[self.lmu_cinema_id])),
            images=[
                CinemaImageTable(
                    cinema_id=self.lmu_cinema_id,
                    url=f"{self.settings.IMAGES_BASE_URL_CINEMAS}/lmu_01.webp",
                    name="LMU Kino"
                )
            ],
            translations=self.lmu_translations
        )
        
    def hm_cinema(self) -> CinemaTable:
        return CinemaTable(
            id=self.hm_cinema_id,
            external_link=HM_CINEMA_URL,
            instagram_link="https://www.instagram.com/hm__kino/",
            location=CinemaLocationTable(**vars(CinemaLocationConstants[self.hm_cinema_id])),
            images=[
                CinemaImageTable(
                    cinema_id=self.hm_cinema_id,
                    url=f"{self.settings.IMAGES_BASE_URL_CINEMAS}/hm_01.webp",
                    name="HM Kino"
                ),
                CinemaImageTable(
                    cinema_id=self.hm_cinema_id,
                    url=f"{self.settings.IMAGES_BASE_URL_CINEMAS}/hm_02.webp",
                    name="HM Kino 2"
                )
            ],
            translations=self.hm_translations
        )
        
    def tum_cinema(self) -> CinemaTable:
        return CinemaTable(
            id=self.tum_cinema_id,
            external_link=TUM_CINEMA_URL,
            instagram_link="https://www.instagram.com/dertufilm/",
            location=CinemaLocationTable(**vars(CinemaLocationConstants[self.tum_cinema_id])),
            images=[
                CinemaImageTable(
                    cinema_id=self.tum_cinema_id,
                    url=f"{self.settings.IMAGES_BASE_URL_CINEMAS}/tum_01.webp",
                    name="TUM Kino"
                ),
                CinemaImageTable(
                    cinema_id=self.tum_cinema_id,
                    url=f"{self.settings.IMAGES_BASE_URL_CINEMAS}/tum_02.webp",
                    name="TUM Kino 2"
                )
            ],
            translations=self.tum_translations
        )
        
    def tum_garching_cinema(self) -> CinemaTable:
        return CinemaTable(
            id=self.tum_garching_cinema_id,
            external_link=TUM_CINEMA_URL,
            instagram_link="https://www.instagram.com/dertufilm/",
            location=CinemaLocationTable(**vars(CinemaLocationConstants[self.tum_garching_cinema_id])),
            translations=self.tum_garching_translations
        )
    
    
    
    lmu_translations = [
        CinemaTranslationTable(
            cinema_id=lmu_cinema_id,
            language=LanguageEnum.GERMAN.value,
            title="U Kino",
            description=[
                CinemaDescription(
                    emoji="🍿",
                    description="Eigene Snacks erlaubt"
                ).model_dump(),
                CinemaDescription(
                    emoji="🎟️",
                    description="Keine Vorverkauf- und Reservierungsmöglichkeit"
                ).model_dump(),
                CinemaDescription(
                    emoji="☁️",
                    description="Erste Besucher erhalten ein Kissen"
                ).model_dump()
            ],
        ),
        CinemaTranslationTable(
            cinema_id=lmu_cinema_id,
            language=LanguageEnum.ENGLISH_US.value,
            title="U Kino",
            description=[
                CinemaDescription(
                    emoji="🍿",
                    description="Bring you own snacks"
                ).model_dump(),
                CinemaDescription(
                    emoji="🎟️",
                    description="No presale, and reservation"
                ).model_dump(),
                CinemaDescription(
                    emoji="☁️",
                    description="Free pillow for first visitors"
                ).model_dump()
            ],
        )
    ]
    
    tum_translations = [
        CinemaTranslationTable(
            cinema_id=tum_cinema_id,
            language=LanguageEnum.GERMAN.value,
            title="TU Film",
            description=[
                CinemaDescription(
                    emoji="🍿",
                    description="Eigene Snacks erlaubt"
                ).model_dump(),
                CinemaDescription(
                    emoji="🎟️",
                    description="Online vorverkauf"
                ).model_dump(),
                CinemaDescription(
                    emoji="👫",
                    description="Offen für Alle"
                ).model_dump()
            ],
        ),
        CinemaTranslationTable(
            cinema_id=tum_cinema_id,
            language=LanguageEnum.ENGLISH_US.value,
            title="TU Film",
            description=[
                CinemaDescription(
                    emoji="🍿",
                    description="Own snacks allowed"
                ).model_dump(),
                CinemaDescription(
                    emoji="🎟️",
                    description="Online presale"
                ).model_dump(),
                CinemaDescription(
                    emoji="👫",
                    description="Open for non-students"
                ).model_dump()
            ],
        )
    ]
    
    tum_garching_translations = [
        CinemaTranslationTable(
            cinema_id=tum_garching_cinema_id,
            language=LanguageEnum.GERMAN.value,
            title="TU Film Garching",
            description=[
                CinemaDescription(
                    emoji="🍿",
                    description="Eigene Snacks erlaubt"
                ).model_dump(),
                CinemaDescription(
                    emoji="🎟️",
                    description="Online vorverkauf"
                ).model_dump(),
                CinemaDescription(
                    emoji="👫",
                    description="Offen für Alle"
                ).model_dump()
            ],
        ),
        CinemaTranslationTable(
            cinema_id=tum_garching_cinema_id,
            language=LanguageEnum.ENGLISH_US.value,
            title="TU Film Garching",
            description=[
                CinemaDescription(
                    emoji="🍿",
                    description="Own snacks allowed"
                ).model_dump(),
                CinemaDescription(
                    emoji="🎟️",
                    description="Online presale"
                ).model_dump(),
                CinemaDescription(
                    emoji="👫",
                    description="Open for non-students"
                ).model_dump()
            ],
        )
    ]
    
    
    hm_translations = [
        CinemaTranslationTable(
            cinema_id=hm_cinema_id,
            language=LanguageEnum.GERMAN.value,
            title="HM Kino",
            description=[
                CinemaDescription(
                    emoji="🍿",
                    description="Eigene Snacks erlaubt"
                ).model_dump(),
                CinemaDescription(
                    emoji="🎟️",
                    description="(Vor)verkauf vor Ort"
                ).model_dump()
            ],
        ),
        CinemaTranslationTable(
            cinema_id=hm_cinema_id,
            language=LanguageEnum.ENGLISH_US.value,
            title="HM Cinema",
            description=[
                CinemaDescription(
                    emoji="🍿",
                    description="Own snacks allowed"
                ).model_dump(),
                CinemaDescription(
                    emoji="🎟️",
                    description="Offline presale"
                ).model_dump()
            ],
        )
    ]
    

    
    
    
    