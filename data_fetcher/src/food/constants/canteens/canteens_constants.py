from shared.src.enums import CanteenEnum
from shared.src.models import Canteen


class CanteensConstants:
    canteens = [
        Canteen(
            id=CanteenEnum.MENSA_LEOPOLDSTR,
            url_id=411,
        ),
        Canteen(
            id=CanteenEnum.MENSA_LOTHSTR,
            url_id=431,
        ),
        Canteen(
            id=CanteenEnum.MENSA_ARCISSTR,
            url_id=421,
        ),
        Canteen(
            id=CanteenEnum.MENSA_GARCHING,
            url_id=422,
        ),
        Canteen(
            id=CanteenEnum.MENSA_MARTINSRIED,
            url_id=412,
        ),
        Canteen(
            id=CanteenEnum.MENSA_PASING,
            url_id=432,
        ),
        Canteen(
            id=CanteenEnum.MENSA_WEIHENSTEPHAN,
            url_id=423,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_ARCISSTR,
            url_id=450,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_BENEDIKTBEUREN,
            url_id=417,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_SCHELLINGSTR,
            url_id=416,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_GOETHESTR,
            url_id=418,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_BUTENANDSTR,
            url_id=414,
        ),
        Canteen(
            id=CanteenEnum.MENSA_ROSENHEIM,
            url_id=441,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_AKADEMIESTR,
            url_id=455,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_KARLSTR,
            url_id=453,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_SCHILLERSTR,
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_AKADEMIE_WEIHENSTEPHAN,
            url_id=456,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_OETTINGENSTR,
            url_id=424,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_ADALBERTSTR,
            url_id=452,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_OLYMPIACAMPUS,
            url_id=425,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_EICHINGER_PLATZ,
            url_id=451,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_MARTINSRIED,
            url_id=415,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN15,
            url_id=457,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN19,
            url_id=426,
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_OBERSCHLEISSHEIM,
            url_id=419,
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_ARCISSTR,
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_LEOPOLDSTR,
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_PASING,
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_WEIHENSTEPHAN_MAXIMUS,
            url_id=525,
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_LOTHSTR,
            url_id=533,
        ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_LEOPOLDSTR,
        #     name="Leopoldstraße",
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_LEOPOLDSTR)
        # ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_OLYMPIACAMPUS,
        #     name="Olympiacampus",
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_OLYMPIACAMPUS)
        # ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_ARCISSTR,
        #     name="Arcisstraße",
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_ARCISSTR)
        # ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_MARTINSRIED,
        #     name="Martinsried",
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_MARTINSRIED)
        # ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_BUTENANDSTR,
        #     name="Butenandstraße",
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_BUTENANDSTR)
        # ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_ROSENHEIM,
        #     name="Rosenheim",
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_ROSENHEIM)
        # ),
        # Canteen(
        #     id=CanteenEnum.STULOUNGE_WEIHENSTEPHAN,
        #     name="Weihenstephan",
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_WEIHENSTEPHAN)
        # ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_LUDWIGSTR,
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_MARTINSRIED,
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_GARCHING_APE,
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_GARCHING,
            url_id=None,
        ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_WEIHENSTEPHAN,
            url_id=None,
        ),
        # Canteen(
        #     id=CanteenEnum.FMI_BISTRO,
        #     name="FMI",
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.FMI_BISTRO)
        # ),
        # Canteen(
        #     id=CanteenEnum.MEDIZINER_MENSA,
        #     name="Mediziner",
        #     opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MEDIZINER_MENSA)
        # ),
        # Canteen(
        #     id=CanteenEnum.IPP_BISTRO,
        #     name="IPP Bistro",
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
