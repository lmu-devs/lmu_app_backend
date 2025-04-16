from data_fetcher.src.food.constants.canteens.canteen_locations_constants import (
    CanteenLocationsConstants,
)
from data_fetcher.src.food.constants.canteens.canteen_opening_hours_constants import (
    CanteenOpeningHoursConstants,
)
from shared.src.enums import CanteenEnum, CanteenTypeEnum
from shared.src.models import Canteen


class CanteensConstants:
    canteens = [
        Canteen(
            id=CanteenEnum.MENSA_LEOPOLDSTR,
            name="Leopoldstraße",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_LEOPOLDSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_LEOPOLDSTR),
            url_id=411,
        ),
        Canteen(
            id=CanteenEnum.MENSA_LOTHSTR,
            name="Lothstraße",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_LOTHSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_LOTHSTR),
            url_id=431,
        ),
        Canteen(
            id=CanteenEnum.MENSA_ARCISSTR,
            name="Arcisstraße",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_ARCISSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_ARCISSTR),
            url_id=421,
        ),
        Canteen(
            id=CanteenEnum.MENSA_GARCHING,
            name="Garching",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_GARCHING),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_GARCHING),
            url_id=422,
        ),
        Canteen(
            id=CanteenEnum.MENSA_MARTINSRIED,
            name="Martinsried",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_MARTINSRIED),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_MARTINSRIED),
            url_id=412,
        ),
        Canteen(
            id=CanteenEnum.MENSA_PASING,
            name="Pasing",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_PASING),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_PASING),
            url_id=432,
        ),
        Canteen(
            id=CanteenEnum.MENSA_WEIHENSTEPHAN,
            name="Weihenstephan",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_WEIHENSTEPHAN),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_WEIHENSTEPHAN),
            url_id=423,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_ARCISSTR,
            name="Arcisstraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_ARCISSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_ARCISSTR),
            url_id=450,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_BENEDIKTBEUREN,
            name="Benediktbeuren",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_BENEDIKTBEUREN),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_BENEDIKTBEUREN),
            url_id=417,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_SCHELLINGSTR,
            name="Schellingstraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_SCHELLINGSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_SCHELLINGSTR),
            url_id=416,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_GOETHESTR,
            name="Goethestraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_GOETHESTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_GOETHESTR),
            url_id=418,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_BUTENANDSTR,
            name="Butenandstraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_BUTENANDSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_BUTENANDSTR),
            url_id=414,
        ),
        Canteen(
            id=CanteenEnum.MENSA_ROSENHEIM,
            name="Rosenheim",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_ROSENHEIM),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_ROSENHEIM),
            url_id=441,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_AKADEMIESTR,
            name="Akademiestraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_AKADEMIESTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_AKADEMIESTR),
            url_id=455,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_KARLSTR,
            name="Karlstraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_KARLSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_KARLSTR),
            url_id=453,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_SCHILLERSTR,
            name="Schillerstraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_SCHILLERSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_SCHILLERSTR),
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_AKADEMIE_WEIHENSTEPHAN,
            name="Weihenstephan Akademie",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_AKADEMIE_WEIHENSTEPHAN),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_AKADEMIE_WEIHENSTEPHAN),
            url_id=456,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_OETTINGENSTR,
            name="Oettingenstraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_OETTINGENSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_OETTINGENSTR),
            url_id=424,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_ADALBERTSTR,
            name="Adalbertstraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_ADALBERTSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_ADALBERTSTR),
            url_id=452,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_OLYMPIACAMPUS,
            name="Olympiacampus",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_OLYMPIACAMPUS),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_OLYMPIACAMPUS),
            url_id=425,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_EICHINGER_PLATZ,
            name="Eichinger Platz",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_EICHINGER_PLATZ),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_EICHINGER_PLATZ),
            url_id=451,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_MARTINSRIED,
            name="Martinsried",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_MARTINSRIED),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_MARTINSRIED),
            url_id=415,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN15,
            name="Garching Boltzmannstr 15",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN15),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN15),
            url_id=457,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN19,
            name="Garching Boltzmannstr 19",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN19),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN19),
            url_id=426,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_OBERSCHLEISSHEIM,
            name="Oberschleissheim",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_OBERSCHLEISSHEIM),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_OBERSCHLEISSHEIM),
            url_id=419,
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_ARCISSTR,
            name="Arcisstraße",
            type=CanteenTypeEnum.STUCAFE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUCAFE_ARCISSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUCAFE_ARCISSTR),
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_LEOPOLDSTR,
            name="Leopoldstraße",
            type=CanteenTypeEnum.STUCAFE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUCAFE_LEOPOLDSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUCAFE_LEOPOLDSTR),
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_PASING,
            name="Pasing",
            type=CanteenTypeEnum.STUCAFE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUCAFE_PASING),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUCAFE_PASING),
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_WEIHENSTEPHAN_MAXIMUS,
            name="Weihenstephan Maximus",
            type=CanteenTypeEnum.STUCAFE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUCAFE_WEIHENSTEPHAN_MAXIMUS),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUCAFE_WEIHENSTEPHAN_MAXIMUS),
            url_id=525,
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_LOTHSTR,
            name="Lothstraße",
            type=CanteenTypeEnum.STUCAFE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUCAFE_LOTHSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUCAFE_LOTHSTR),
            url_id=533,
        ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_LEOPOLDSTR,
        #     name="Leopoldstraße",
        #     type=CanteenTypeEnum.STULOUNGE,
        #     location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_LEOPOLDSTR),
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_LEOPOLDSTR)
        # ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_OLYMPIACAMPUS,
        #     name="Olympiacampus",
        #     type=CanteenTypeEnum.STULOUNGE,
        #     location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_OLYMPIACAMPUS),
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_OLYMPIACAMPUS)
        # ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_ARCISSTR,
        #     name="Arcisstraße",
        #     type=CanteenTypeEnum.STULOUNGE,
        #     location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_ARCISSTR),
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_ARCISSTR)
        # ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_MARTINSRIED,
        #     name="Martinsried",
        #     type=CanteenTypeEnum.STULOUNGE,
        #     location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_MARTINSRIED),
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_MARTINSRIED)
        # ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_BUTENANDSTR,
        #     name="Butenandstraße",
        #     type=CanteenTypeEnum.STULOUNGE,
        #     location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_BUTENANDSTR),
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_BUTENANDSTR)
        # ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_ROSENHEIM,
        #     name="Rosenheim",
        #     type=CanteenTypeEnum.STULOUNGE,
        #     location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_ROSENHEIM),
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_ROSENHEIM)
        # ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_WEIHENSTEPHAN,
        #     name="Weihenstephan",
        #     type=CanteenTypeEnum.STULOUNGE,
        #     location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_WEIHENSTEPHAN),
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_WEIHENSTEPHAN)
        # ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_LUDWIGSTR,
            name="Ludwigstraße",
            type=CanteenTypeEnum.ESPRESSOBAR,
            location=CanteenLocationsConstants.get_location(CanteenEnum.ESPRESSOBAR_LUDWIGSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.ESPRESSOBAR_LUDWIGSTR),
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_MARTINSRIED,
            name="Martinsried",
            type=CanteenTypeEnum.ESPRESSOBAR,
            location=CanteenLocationsConstants.get_location(CanteenEnum.ESPRESSOBAR_MARTINSRIED),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.ESPRESSOBAR_MARTINSRIED),
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_GARCHING_APE,
            name="Garching Ape",
            type=CanteenTypeEnum.ESPRESSOBAR,
            location=CanteenLocationsConstants.get_location(CanteenEnum.ESPRESSOBAR_GARCHING_APE),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.ESPRESSOBAR_GARCHING_APE),
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_GARCHING,
            name="Garching",
            type=CanteenTypeEnum.ESPRESSOBAR,
            location=CanteenLocationsConstants.get_location(CanteenEnum.ESPRESSOBAR_GARCHING),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.ESPRESSOBAR_GARCHING),
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_WEIHENSTEPHAN,
            name="Weihenstephan",
            type=CanteenTypeEnum.ESPRESSOBAR,
            location=CanteenLocationsConstants.get_location(CanteenEnum.ESPRESSOBAR_WEIHENSTEPHAN),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.ESPRESSOBAR_WEIHENSTEPHAN),
            url_id=None,
        ),
        # Canteen(
        #     id=CanteenEnum.FMI_BISTRO,
        #     name="FMI",
        #     type=CanteenTypeEnum.STUBISTRO,
        #     location=CanteenLocationsConstants.get_location(CanteenEnum.FMI_BISTRO),
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.FMI_BISTRO)
        # ),
        # Canteen(
        #     id=CanteenEnum.MEDIZINER_MENSA,
        #     name="Mediziner",
        #     type=CanteenTypeEnum.MENSA,
        #     location=CanteenLocationsConstants.get_location(CanteenEnum.MEDIZINER_MENSA),
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MEDIZINER_MENSA)
        # ),
        # Canteen(
        #     id=CanteenEnum.IPP_BISTRO,
        #     name="IPP Bistro",
        #     type=CanteenTypeEnum.STUBISTRO,
        #     location=CanteenLocationsConstants.get_location(CanteenEnum.IPP_BISTRO),
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.IPP_BISTRO)
        # ),
    ]

    @classmethod
    def get_canteen(cls, canteen_enum: CanteenEnum) -> Canteen:
        """
        Returns a specific canteen based on its enum value.

        Args:
            canteen_enum (CanteenEnum): The enum value of the desired canteen

        Returns:
            Canteen: The matching canteen object

        Raises:
            ValueError: If no canteen is found for the given enum
        """
        for canteen in cls.canteens:
            if canteen.id == canteen_enum:
                return canteen
        raise ValueError(f"No canteen found for enum: {canteen_enum}")
