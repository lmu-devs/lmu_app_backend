from shared.src.enums.canteen_enums import CanteenEnum
from shared.src.models import Location

rosenheim_locations = {
    CanteenEnum.MENSA_ROSENHEIM: Location(
        address="Hochschulstr. 1, 83024 Rosenheim",
        latitude=47.867723,
        longitude=12.107417,
    ),
    # CanteenEnum.STULOUNGE_ROSENHEIM: Location(
    #     address="Hochschulstr. 1, 83024 Rosenheim",
    #     latitude=47.867723,
    #     longitude=12.107417
    # ),
}
