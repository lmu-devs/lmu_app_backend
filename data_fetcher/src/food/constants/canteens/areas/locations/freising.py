from shared.src.enums.canteen_enums import CanteenEnum
from shared.src.models import Location

freising_locations = {
    CanteenEnum.MENSA_WEIHENSTEPHAN: Location(
        address="Maximus-von-Imhof-Forum 5, 85354 Freising",
        latitude=48.399537,
        longitude=11.723210,
    ),
    CanteenEnum.STUCAFE_WEIHENSTEPHAN_MAXIMUS: Location(
        address="Maximus-von-Imhof-Forum 5, 85354 Freising",
        latitude=48.399537,
        longitude=11.723210,
    ),
    CanteenEnum.STUBISTRO_AKADEMIE_WEIHENSTEPHAN: Location(
        address="Alte Akademie 1, 85354 Freising",
        latitude=48.395008,
        longitude=11.729333,
    ),
    CanteenEnum.ESPRESSOBAR_WEIHENSTEPHAN: Location(
        address="Maximus-von-Imhof-Forum 5, 85354 Freising",
        latitude=48.399537,
        longitude=11.723210,
    ),
    # CanteenEnum.STULOUNGE_WEIHENSTEPHAN: Location(
    #     address="Am Staudengarten 1, 85354 Freising",
    #     latitude=48.399021,
    #     longitude=11.728100
    # )
}
