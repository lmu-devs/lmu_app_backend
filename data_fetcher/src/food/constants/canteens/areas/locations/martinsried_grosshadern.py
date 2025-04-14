from shared.src.enums.canteen_enums import CanteenEnum
from shared.src.models import Location

martinsried_grosshadern_locations = {
    CanteenEnum.MENSA_MARTINSRIED: Location(
        address="Großhaderner Str. 6 , 82152 Planegg-Martinsried",
        latitude=48.109883,
        longitude=11.459971,
    ),
    CanteenEnum.STUBISTRO_MARTINSRIED: Location(
        address="Großhadernerstr. 9a,  82152 Planegg-Martinsried",
        latitude=48.109972,
        longitude=11.458483,
    ),
    # CanteenEnum.STULOUNGE_MARTINSRIED: Location(
    #     address="Großhadernerstr. 9,  82152 Planegg-Martinsried",
    #     latitude=48.110548,
    #     longitude=11.458981
    # ),
    CanteenEnum.ESPRESSOBAR_MARTINSRIED: Location(
        address="Großhaderner Str. 2, 82152 Planegg-Martinsried",
        latitude=48.109025,
        longitude=11.458656,
    ),
    CanteenEnum.STUBISTRO_BUTENANDSTR: Location(
        address="Butenandtstr. 13, Gebäude F, 81375 München",
        latitude=48.113644,
        longitude=11.466461,
    ),
    # CanteenEnum.STULOUNGE_BUTENANDSTR: Location(
    #     address="Butenandtstr. 1 , 81377 München",
    #     latitude=48.114105,
    #     longitude=11.464837
    # ),
}
