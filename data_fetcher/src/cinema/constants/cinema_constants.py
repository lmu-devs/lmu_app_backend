from shared.src.core.settings import get_settings
from shared.src.enums import CinemaEnum, LanguageEnum
from shared.src.tables import (
    CinemaImageTable,
    CinemaLocationTable,
    CinemaTable,
    CinemaTranslationTable,
)

from ..constants.location_constants import CinemaLocationConstants
from ..constants.url_constants import HM_CINEMA_URL, LMU_CINEMA_URL, TUM_CINEMA_URL
from ..models.cinema_description_model import CinemaDescription

_settings = get_settings()

lmu_cinema = CinemaTable(
    id=CinemaEnum.LMU.value,
    external_link=LMU_CINEMA_URL,
    instagram_link="https://www.instagram.com/das.ukino/",
    location=CinemaLocationTable(**vars(CinemaLocationConstants[CinemaEnum.LMU.value])),
    images=[
        CinemaImageTable(
            cinema_id=CinemaEnum.LMU.value,
            url=f"{_settings.IMAGES_BASE_URL_CINEMAS}/lmu_01.webp",
            name="LMU Kino",
        ),
        CinemaImageTable(
            cinema_id=CinemaEnum.LMU.value,
            url=f"{_settings.IMAGES_BASE_URL_CINEMAS}/lmu_02.webp",
            name="LMU Kino 2",
        ),
    ],
    translations=[
        CinemaTranslationTable(
            cinema_id=CinemaEnum.LMU.value,
            language=LanguageEnum.GERMAN.value,
            title="U Kino",
            description=[
                CinemaDescription(emoji="🍿", description="Eigene Snacks erlaubt").model_dump(),
                CinemaDescription(
                    emoji="🎟️",
                    description="Keine Vorverkauf- und Reservierungsmöglichkeit",
                ).model_dump(),
                CinemaDescription(emoji="☁️", description="Erste Besucher erhalten ein Kissen").model_dump(),
            ],
        ),
        CinemaTranslationTable(
            cinema_id=CinemaEnum.LMU.value,
            language=LanguageEnum.ENGLISH_US.value,
            title="U Kino",
            description=[
                CinemaDescription(emoji="🍿", description="Bring you own snacks").model_dump(),
                CinemaDescription(emoji="🎟️", description="No presale, and reservation").model_dump(),
                CinemaDescription(emoji="☁️", description="Free pillow for first visitors").model_dump(),
            ],
        ),
    ],
)

hm_cinema = CinemaTable(
    id=CinemaEnum.HM.value,
    external_link=HM_CINEMA_URL,
    instagram_link="https://www.instagram.com/hm__kino/",
    location=CinemaLocationTable(**vars(CinemaLocationConstants[CinemaEnum.HM.value])),
    images=[
        CinemaImageTable(
            cinema_id=CinemaEnum.HM.value,
            url=f"{_settings.IMAGES_BASE_URL_CINEMAS}/hm_01.webp",
            name="HM Kino",
        ),
        CinemaImageTable(
            cinema_id=CinemaEnum.HM.value,
            url=f"{_settings.IMAGES_BASE_URL_CINEMAS}/hm_02.webp",
            name="HM Kino 2",
        ),
    ],
    translations=[
        CinemaTranslationTable(
            cinema_id=CinemaEnum.HM.value,
            language=LanguageEnum.GERMAN.value,
            title="HM Kino",
            description=[
                CinemaDescription(emoji="🍿", description="Eigene Snacks erlaubt").model_dump(),
                CinemaDescription(emoji="🎟️", description="(Vor)verkauf vor Ort").model_dump(),
            ],
        ),
        CinemaTranslationTable(
            cinema_id=CinemaEnum.HM.value,
            language=LanguageEnum.ENGLISH_US.value,
            title="HM Cinema",
            description=[
                CinemaDescription(emoji="🍿", description="Own snacks allowed").model_dump(),
                CinemaDescription(emoji="🎟️", description="Offline presale").model_dump(),
            ],
        ),
    ],
)

tum_cinema = CinemaTable(
    id=CinemaEnum.TUM.value,
    external_link=TUM_CINEMA_URL,
    instagram_link="https://www.instagram.com/dertufilm/",
    location=CinemaLocationTable(**vars(CinemaLocationConstants[CinemaEnum.TUM.value])),
    images=[
        CinemaImageTable(
            cinema_id=CinemaEnum.TUM.value,
            url=f"{_settings.IMAGES_BASE_URL_CINEMAS}/tum_01.webp",
            name="TUM Kino",
        ),
        CinemaImageTable(
            cinema_id=CinemaEnum.TUM.value,
            url=f"{_settings.IMAGES_BASE_URL_CINEMAS}/tum_02.webp",
            name="TUM Kino 2",
        ),
    ],
    translations=[
        CinemaTranslationTable(
            cinema_id=CinemaEnum.TUM.value,
            language=LanguageEnum.GERMAN.value,
            title="TU Film",
            description=[
                CinemaDescription(emoji="🍿", description="Eigene Snacks erlaubt").model_dump(),
                CinemaDescription(emoji="🎟️", description="Online vorverkauf").model_dump(),
                CinemaDescription(emoji="👫", description="Offen für Alle").model_dump(),
            ],
        ),
        CinemaTranslationTable(
            cinema_id=CinemaEnum.TUM.value,
            language=LanguageEnum.ENGLISH_US.value,
            title="TU Film",
            description=[
                CinemaDescription(emoji="🍿", description="Own snacks allowed").model_dump(),
                CinemaDescription(emoji="🎟️", description="Online presale").model_dump(),
                CinemaDescription(emoji="👫", description="Open for non-students").model_dump(),
            ],
        ),
    ],
)

tum_garching_cinema = CinemaTable(
    id=CinemaEnum.TUM_GARCHING.value,
    external_link=TUM_CINEMA_URL,
    instagram_link="https://www.instagram.com/dertufilm/",
    location=CinemaLocationTable(**vars(CinemaLocationConstants[CinemaEnum.TUM_GARCHING.value])),
    translations=[
        CinemaTranslationTable(
            cinema_id=CinemaEnum.TUM_GARCHING.value,
            language=LanguageEnum.GERMAN.value,
            title="TU Film Garching",
            description=[
                CinemaDescription(emoji="🍿", description="Eigene Snacks erlaubt").model_dump(),
                CinemaDescription(emoji="🎟️", description="Online vorverkauf").model_dump(),
                CinemaDescription(emoji="👫", description="Offen für Alle").model_dump(),
            ],
        ),
        CinemaTranslationTable(
            cinema_id=CinemaEnum.TUM_GARCHING.value,
            language=LanguageEnum.ENGLISH_US.value,
            title="TU Film Garching",
            description=[
                CinemaDescription(emoji="🍿", description="Own snacks allowed").model_dump(),
                CinemaDescription(emoji="🎟️", description="Online presale").model_dump(),
                CinemaDescription(emoji="👫", description="Open for non-students").model_dump(),
            ],
        ),
    ],
)
