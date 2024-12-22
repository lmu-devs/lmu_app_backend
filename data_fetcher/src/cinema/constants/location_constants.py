from shared.src.enums import UniversityEnum
from shared.src.schemas import Location

CinemaLocationConstants = {
    UniversityEnum.LMU: Location(
        address="Max-Joseph-Platz 11, 80539 München",
        latitude=48.1351,
        longitude=11.5761,
    ),
    UniversityEnum.HM: Location(
        address="Hörsaal B052, Theresienstraße 37-39",
        latitude=48.147902,
        longitude=11.573249,
    ),
}
