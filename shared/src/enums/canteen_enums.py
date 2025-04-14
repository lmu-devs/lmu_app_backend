from enum import Enum


class CanteenTypeEnum(str, Enum):
    MENSA = "MENSA"
    STUBISTRO = "STUBISTRO"
    STUCAFE = "STUCAFE"
    STULOUNGE = "STULOUNGE"
    ESPRESSOBAR = "ESPRESSOBAR"


class CanteenEnum(str, Enum):
    MENSA_LEOPOLDSTR = "mensa-leopoldstr"
    MENSA_LOTHSTR = "mensa-lothstr"
    MENSA_ARCISSTR = "mensa-arcisstr"
    MENSA_GARCHING = "mensa-garching"
    MENSA_MARTINSRIED = "mensa-martinsried"
    MENSA_PASING = "mensa-pasing"
    MENSA_WEIHENSTEPHAN = "mensa-weihenstephan"
    MENSA_ROSENHEIM = "mensa-rosenheim"

    STUBISTRO_AKADEMIESTR = "stubistro-akademiestr"
    STUBISTRO_SCHELLINGSTR = "stubistro-schellingstr"
    STUBISTRO_ARCISSTR = "stubistro-arcisstr"
    STUBISTRO_GOETHESTR = "stubistro-goethestr"
    STUBISTRO_BUTENANDSTR = "stubistro-butenandstr"
    STUBISTRO_MARTINSRIED = "stubistro-martinsried"

    STUBISTRO_AKADEMIE_WEIHENSTEPHAN = "stubistro-akademie-weihenstephan"
    STUBISTRO_KARLSTR = "stucafe-karlstr"

    ## TUM API not working
    STUBISTRO_SCHILLERSTR = "stubistro-schillerstr"
    STUBISTRO_OETTINGENSTR = "stubistro-oettingenstr"
    STUBISTRO_ADALBERTSTR = "stubistro-adalbertstr"
    STUBISTRO_OLYMPIACAMPUS = "stubistro-olympiacampus"  # = stucafe-connollystr
    STUBISTRO_EICHINGER_PLATZ = "stubistro-eichinger-platz"
    STUBISTRO_GARCHING_BOLTZMANN15 = "stubistro-garching-boltzmann15"
    STUBISTRO_GARCHING_BOLTZMANN19 = "stubistro-garching-boltzmann19"
    STUBISTRO_OBERSCHLEISSHEIM = "stubistro-oberschleissheim"
    STUBISTRO_BENEDIKTBEUREN = "stubistro-benediktbeuren"

    STUCAFE_ARCISSTR = "stucafe-arcisstr"
    STUCAFE_LEOPOLDSTR = "stucafe-leopoldstr"
    STUCAFE_PASING = "stucafe-pasing"
    STUCAFE_WEIHENSTEPHAN_MAXIMUS = "stucafe-weihenstephan-maximus"
    STUCAFE_LOTHSTR = "stucafe-lothstr"

    # STULOUNGE_LEOPOLDSTR = "stulounge-leopoldstr"
    # STULOUNGE_OLYMPIACAMPUS = "stulounge-olympiacampus"
    # STULOUNGE_ARCISSTR = "stulounge-arcisstr"
    # STULOUNGE_MARTINSRIED = "stulounge-martinsried"
    # STULOUNGE_BUTENANDSTR = "stulounge-butenandstr"
    # STULOUNGE_ROSENHEIM = "stulounge-rosenheim"
    # STULOUNGE_WEIHENSTEPHAN = "stulounge-weihenstephan"

    ESPRESSOBAR_LUDWIGSTR = "espressobar-ludwigstr"
    ESPRESSOBAR_MARTINSRIED = "espressobar-martinsried"
    ESPRESSOBAR_GARCHING_APE = "espressobar-garching-ape"
    ESPRESSOBAR_GARCHING = "espressobar-garching"
    ESPRESSOBAR_WEIHENSTEPHAN = "espressobar-weihenstephan"

    def get_active_canteens():
        return [
            CanteenEnum.MENSA_ARCISSTR,
            CanteenEnum.MENSA_GARCHING,
            CanteenEnum.MENSA_LEOPOLDSTR,
            CanteenEnum.MENSA_LOTHSTR,
            CanteenEnum.MENSA_MARTINSRIED,
            CanteenEnum.MENSA_PASING,
            CanteenEnum.MENSA_ROSENHEIM,
            CanteenEnum.MENSA_WEIHENSTEPHAN,
            CanteenEnum.STUBISTRO_ADALBERTSTR,
            CanteenEnum.STUBISTRO_AKADEMIESTR,
            CanteenEnum.STUBISTRO_ARCISSTR,
            CanteenEnum.STUBISTRO_BENEDIKTBEUREN,
            CanteenEnum.STUBISTRO_EICHINGER_PLATZ,
            CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN15,
            CanteenEnum.STUBISTRO_BUTENANDSTR,
            CanteenEnum.STUBISTRO_GARCHING_BOLTZMANN19,
            CanteenEnum.STUBISTRO_GOETHESTR,
            CanteenEnum.STUBISTRO_KARLSTR,
            CanteenEnum.STUBISTRO_MARTINSRIED,
            CanteenEnum.STUBISTRO_OBERSCHLEISSHEIM,
            CanteenEnum.STUBISTRO_OETTINGENSTR,
            CanteenEnum.STUBISTRO_OLYMPIACAMPUS,
            CanteenEnum.STUBISTRO_SCHELLINGSTR,
            CanteenEnum.STUBISTRO_SCHILLERSTR,
            CanteenEnum.STUBISTRO_AKADEMIE_WEIHENSTEPHAN,
            CanteenEnum.STUCAFE_LOTHSTR,
            CanteenEnum.STUCAFE_WEIHENSTEPHAN_MAXIMUS,
        ]

    @classmethod
    def get_active_canteens_values(cls):
        return [canteen.value for canteen in cls.get_active_canteens()]

    ## Sort out
    # MEDIZINER_MENSA = "mediziner-mensa"
    # FMI_BISTRO = "fmi-bistro"
    # IPP_BISTRO = "ipp-bistro"
    # MENSA_BILDUNGSCAMPUS_HEILBRONN = "mensa-bildungscampus-heilbronn"
    # MENSA_STRAUBING = "mensa-straubing"
