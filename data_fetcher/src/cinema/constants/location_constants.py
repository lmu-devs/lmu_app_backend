from shared.src.schemas import Location
from shared.src.enums import CinemaEnums
CinemaLocationConstants = {
    CinemaEnums.LMU.value: Location(
        address="Hörsaal B052,Max-Joseph-Platz 11, München",
        latitude=48.1351,
        longitude=11.5761,
    ),
    CinemaEnums.HM.value: Location(
        address="Hörsaal B052, Theresienstraße 37-39, München",
        latitude=48.147902,
        longitude=11.573249,
    ),
    CinemaEnums.TUM.value: Location(
        address="Carl-von-Linde-Hörsaal 1200 - Stadt, Arcisstraße 21, München",
        latitude=48.1480344,
        longitude=11.5679141,
    ),
    CinemaEnums.TUM_GARCHING.value: Location(
        address="Hörsaal MW 1801, Boltzmannstraße 15, Garching",
        latitude=48.265851,
        longitude=11.667809,
    ),
}
