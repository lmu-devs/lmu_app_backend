from shared.src.enums.canteen_enums import CanteenEnum
from shared.src.models import Location

munich_locations = {
    CanteenEnum.MENSA_LEOPOLDSTR: Location(
        address="Leopoldstr. 13a, 80802 München",
        latitude=48.15632028888637,
        longitude=11.582507004053339,
    ),
    CanteenEnum.STUCAFE_LEOPOLDSTR: Location(
        address="Leopoldstr. 13a, 80802 München",
        latitude=48.156580923447166,
        longitude=11.581929225099229,
    ),
    # CanteenEnum.STULOUNGE_LEOPOLDSTR: Location(
    #     address="Leopoldstr. 13a, 80802 München",
    #     latitude=48.156404,
    #     longitude=11.582161
    # ),
    CanteenEnum.STUBISTRO_OETTINGENSTR: Location(
        address="Oettingenstraße. 67, 80538 München",
        latitude=48.149910,
        longitude=11.594334,
    ),
    CanteenEnum.STUBISTRO_ADALBERTSTR: Location(
        address="Adalbertstr. 5, 80799 München", latitude=48.151675, longitude=11.579688
    ),
    CanteenEnum.ESPRESSOBAR_LUDWIGSTR: Location(
        address="Ludwigstr. 28, 80539 München",
        latitude=48.1509446875566,
        longitude=11.582763147212601,
    ),
    CanteenEnum.STUBISTRO_AKADEMIESTR: Location(
        address="Akademiestraße 2-4, 80799 München",
        latitude=48.153099,
        longitude=11.580270,
    ),
    CanteenEnum.STUBISTRO_SCHELLINGSTR: Location(
        address="Schellingstr. 3, 80799 München",
        latitude=48.149198,
        longitude=11.579225,
    ),
    CanteenEnum.STUBISTRO_SCHILLERSTR: Location(
        address="Schillerstr. 47, 80336 München",
        latitude=48.134633,
        longitude=11.561170,
    ),
    CanteenEnum.STUBISTRO_GOETHESTR: Location(
        address="Goethestr. 70, 80336 München", latitude=48.131359, longitude=11.558165
    ),
    CanteenEnum.MENSA_ARCISSTR: Location(
        address="Arcisstr. 17, 80333 München", latitude=48.147371, longitude=11.567019
    ),
    # CanteenEnum.STULOUNGE_ARCISSTR: Location(
    #     address="Arcisstr. 17, 80333 München",
    #     latitude=48.147371,
    #     longitude=11.567019
    # ),
    CanteenEnum.STUBISTRO_ARCISSTR: Location(
        address="Arcisstr. 12, 80333 München", latitude=48.146042, longitude=11.567620
    ),
    CanteenEnum.STUCAFE_ARCISSTR: Location(
        address="Arcisstr. 21, 80333 München", latitude=48.146616, longitude=11.567286
    ),
    CanteenEnum.STUBISTRO_EICHINGER_PLATZ: Location(
        address="Bernd Eichinger Platz 1, 80333 München",
        latitude=48.146670,
        longitude=11.569517,
    ),
    CanteenEnum.STUBISTRO_OLYMPIACAMPUS: Location(
        address="Am Olympiacampus 11, 80809 München",
        latitude=48.179918,
        longitude=11.544748,
    ),
    # CanteenEnum.STULOUNGE_OLYMPIACAMPUS: Location(
    #     address="Am Olympiacampus 11, 80809 München",
    #     latitude=48.181983,
    #     longitude=11.552184
    # ),
    CanteenEnum.MENSA_LOTHSTR: Location(address="Lothstr. 13d, 80335 München", latitude=48.153950, longitude=11.552431),
    CanteenEnum.STUCAFE_LOTHSTR: Location(
        address="Lothstr. 64, 80335 München", latitude=48.155054, longitude=11.555812
    ),
    CanteenEnum.STUBISTRO_KARLSTR: Location(
        address="Karlstr. 6, 80333 München", latitude=48.142697, longitude=11.568428
    ),
}
