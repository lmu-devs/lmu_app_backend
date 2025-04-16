from enum import Enum

from .language_enums import LanguageEnum


class UniversityEnum(str, Enum):
    LMU = "LMU"
    TUM = "TUM"
    HM = "HM"


university_translations = {
    UniversityEnum.LMU: {
        LanguageEnum.GERMAN: "Ludwig-Maximilians-Universität München",
        LanguageEnum.ENGLISH_US: "Ludwig Maximilian University of Munich",
    },
    UniversityEnum.TUM: {
        LanguageEnum.GERMAN: "Technische Universität München",
        LanguageEnum.ENGLISH_US: "Technical University of Munich",
    },
    UniversityEnum.HM: {
        LanguageEnum.GERMAN: "Hochschule München",
        LanguageEnum.ENGLISH_US: "University of Applied Sciences Munich",
    },
}
