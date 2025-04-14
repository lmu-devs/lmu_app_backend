from shared.src.enums.canteen_enums import CanteenEnum
from shared.src.models import Location

garching_locations = {
    CanteenEnum.MENSA_GARCHING: Location(
        address="Boltzmannstr. 19, 85748 Garching",
        latitude=48.268190,
        longitude=11.672119,
    ),
    CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN19: Location(
        address="Boltzmannstr. 19, 85748 Garching",
        latitude=48.268190,
        longitude=11.672119,
    ),
    CanteenEnum.ESPRESSOBAR_GARCHING_APE: Location(
        address="Boltzmannstr. 19, 85748 Garching",
        latitude=48.268190,
        longitude=11.672119,
    ),
    CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN15: Location(
        address="Boltzmannstr. 15, 85748 Garching",
        latitude=48.265664,
        longitude=11.669267,
    ),
    CanteenEnum.ESPRESSOBAR_GARCHING: Location(
        address="Boltzmannstr. 15, 85748 Garching",
        latitude=48.265664,
        longitude=11.669267,
    ),
}
