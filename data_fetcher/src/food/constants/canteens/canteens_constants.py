from shared.src.schemas import Canteen
from shared.src.enums import CanteenEnum, CanteenTypeEnum
from data_fetcher.src.food.constants.canteens.canteen_locations_constants import CanteenLocationsConstants
from data_fetcher.src.food.constants.canteens.canteen_opening_hours_constants import CanteenOpeningHoursConstants

class CanteensConstants:
    canteens = [
        Canteen(
            id=CanteenEnum.MENSA_LEOPOLDSTR,
            name="Leopoldstraße",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_LEOPOLDSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_LEOPOLDSTR)
        ),
        Canteen(
            id=CanteenEnum.MENSA_LOTHSTR,
            name="Lothstraße",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_LOTHSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_LOTHSTR)
        ),
        Canteen(
            id=CanteenEnum.MENSA_ARCISSTR,
            name="Arcisstraße",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_ARCISSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_ARCISSTR)
        ),
        Canteen(
            id=CanteenEnum.MENSA_GARCHING,
            name="Garching",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_GARCHING),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_GARCHING)
        ),
        Canteen(
            id=CanteenEnum.MENSA_MARTINSRIED,
            name="Martinsried",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_MARTINSRIED),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_MARTINSRIED)
        ),
        Canteen(
            id=CanteenEnum.MENSA_PASING,
            name="Pasing",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_PASING),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_PASING)
        ),
        Canteen(
            id=CanteenEnum.MENSA_WEIHENSTEPHAN,
            name="Weihenstephan",
            type=CanteenTypeEnum.MENSA,
            location=CanteenLocationsConstants.get_location(CanteenEnum.MENSA_WEIHENSTEPHAN),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.MENSA_WEIHENSTEPHAN)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_ARCISSTR,
            name="Arcisstraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_ARCISSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_ARCISSTR)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_SCHELLINGSTR,
            name="Schellingstraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_SCHELLINGSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_SCHELLINGSTR)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_GOETHESTR,
            name="Goethestraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_GOETHESTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_GOETHESTR)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_BUTENANDSTR,
            name="Butenandstraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_BUTENANDSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_BUTENANDSTR)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_ROSENHEIM,
            name="Rosenheim",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_ROSENHEIM),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_ROSENHEIM)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_MARTINSRIED,
            name="Martinsried",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_MARTINSRIED),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_MARTINSRIED)
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_AKADEMIE_WEIHENSTEPHAN,
            name="Akademie Weihenstephan",
            type=CanteenTypeEnum.STUCAFE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUCAFE_AKADEMIE_WEIHENSTEPHAN),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUCAFE_AKADEMIE_WEIHENSTEPHAN)
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_KARLSTR,
            name="Karlstraße",
            type=CanteenTypeEnum.STUCAFE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUCAFE_KARLSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUCAFE_KARLSTR)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_SCHILLERSTR,
            name="Schillerstraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_SCHILLERSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_SCHILLERSTR)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_OETTINGENSTR,
            name="Oettingenstraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_OETTINGENSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_OETTINGENSTR)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_ADALBERTSTR,
            name="Adalbertstraße",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_ADALBERTSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_ADALBERTSTR)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_OLYMPIACAMPUS,
            name="Olympiacampus",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_OLYMPIACAMPUS),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_OLYMPIACAMPUS)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_EICHINGER_PLATZ,
            name="Eichinger Platz",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_EICHINGER_PLATZ),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_EICHINGER_PLATZ)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_MARTINSRIED,
            name="Martinsried",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_MARTINSRIED),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_MARTINSRIED)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN15,
            name="Garching Boltzmannstraße 15",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN15),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN15)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN19,
            name="Garching Boltzmannstraße 19",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN19),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN19)
        ),
        Canteen(
            id=CanteenEnum.STUBISTRO_OBERSCHLEISSHEIM,
            name="Oberschleissheim",
            type=CanteenTypeEnum.STUBISTRO,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUBISTRO_OBERSCHLEISSHEIM),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUBISTRO_OBERSCHLEISSHEIM)
        ),
    
        Canteen(
            id=CanteenEnum.STUCAFE_ARCISSTR,
            name="Arcisstraße",
            type=CanteenTypeEnum.STUCAFE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUCAFE_ARCISSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUCAFE_ARCISSTR)
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_LEOPOLDSTR,
            name="Leopoldstraße",
            type=CanteenTypeEnum.STUCAFE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUCAFE_LEOPOLDSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUCAFE_LEOPOLDSTR)
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_PASING,
            name="Pasing",
            type=CanteenTypeEnum.STUCAFE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUCAFE_PASING),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUCAFE_PASING)
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_WEIHENSTEPHAN_MAXIMUS,
            name="Weihenstephan Maximustraße",
            type=CanteenTypeEnum.STUCAFE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUCAFE_WEIHENSTEPHAN_MAXIMUS),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUCAFE_WEIHENSTEPHAN_MAXIMUS)
        ),
        Canteen(
            id=CanteenEnum.STUCAFE_LOTHSTR,
            name="Lothstraße",
            type=CanteenTypeEnum.STUCAFE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STUCAFE_LOTHSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STUCAFE_LOTHSTR)
        ),
    
        Canteen(
            id=CanteenEnum.STULOUNGE_LEOPOLDSTR,
            name="Leopoldstraße",
            type=CanteenTypeEnum.STULOUNGE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_LEOPOLDSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_LEOPOLDSTR)
        ),
        Canteen(
            id=CanteenEnum.STULOUNGE_OLYMPIACAMPUS,
            name="Olympiacampus",
            type=CanteenTypeEnum.STULOUNGE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_OLYMPIACAMPUS),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_OLYMPIACAMPUS)
        ),
        Canteen(
            id=CanteenEnum.STULOUNGE_ARCISSTR,
            name="Arcisstraße",
            type=CanteenTypeEnum.STULOUNGE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_ARCISSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_ARCISSTR)
        ),
        Canteen(
            id=CanteenEnum.STULOUNGE_MARTINSRIED,
            name="Martinsried",
            type=CanteenTypeEnum.STULOUNGE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_MARTINSRIED),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_MARTINSRIED)
        ),
        Canteen(
            id=CanteenEnum.STULOUNGE_BUTENANDSTR,
            name="Butenandstraße",
            type=CanteenTypeEnum.STULOUNGE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_BUTENANDSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_BUTENANDSTR)
        ),
        Canteen(
            id=CanteenEnum.STULOUNGE_ROSENHEIM,
            name="Rosenheim",
            type=CanteenTypeEnum.STULOUNGE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_ROSENHEIM),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_ROSENHEIM)
        ),
        Canteen(
            id=CanteenEnum.STULOUNGE_WEIHENSTEPHAN,
            name="Weihenstephan",
            type=CanteenTypeEnum.STULOUNGE,
            location=CanteenLocationsConstants.get_location(CanteenEnum.STULOUNGE_WEIHENSTEPHAN),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.STULOUNGE_WEIHENSTEPHAN)
        ),
    
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_LUDWIGSTR,
            name="Ludwigstraße",
            type=CanteenTypeEnum.ESPRESSOBAR,
            location=CanteenLocationsConstants.get_location(CanteenEnum.ESPRESSOBAR_LUDWIGSTR),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.ESPRESSOBAR_LUDWIGSTR)
        ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_MARTINSRIED,
            name="Martinsried",
            type=CanteenTypeEnum.ESPRESSOBAR,
            location=CanteenLocationsConstants.get_location(CanteenEnum.ESPRESSOBAR_MARTINSRIED),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.ESPRESSOBAR_MARTINSRIED)
        ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_GARCHING_APE,
            name="Garching Ape",
            type=CanteenTypeEnum.ESPRESSOBAR,
            location=CanteenLocationsConstants.get_location(CanteenEnum.ESPRESSOBAR_GARCHING_APE),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.ESPRESSOBAR_GARCHING_APE)
        ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_GARCHING,
            name="Garching",
            type=CanteenTypeEnum.ESPRESSOBAR,
            location=CanteenLocationsConstants.get_location(CanteenEnum.ESPRESSOBAR_GARCHING),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.ESPRESSOBAR_GARCHING)
        ),
        Canteen(
            id=CanteenEnum.ESPRESSOBAR_WEIHENSTEPHAN,
            name="Weihenstephan",
            type=CanteenTypeEnum.ESPRESSOBAR,
            location=CanteenLocationsConstants.get_location(CanteenEnum.ESPRESSOBAR_WEIHENSTEPHAN),
            opening_hours=CanteenOpeningHoursConstants.get_opening_hours(CanteenEnum.ESPRESSOBAR_WEIHENSTEPHAN)
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
    