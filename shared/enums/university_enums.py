from enum import Enum
from .language_enums import Language

class University(Enum):
    LMU = "lmu"
    TUM = "tum"
    HM = "hm"
    
university_translations = {
    University.LMU: {
        Language.GERMAN: "Ludwig-Maximilians-Universität München",
        Language.ENGLISH_US: "Ludwig Maximilian University of Munich",
    },
    University.TUM: {
        Language.GERMAN: "Technische Universität München",
        Language.ENGLISH_US: "Technical University of Munich",
    },
    University.HM: {
        Language.GERMAN: "Hochschule München",
        Language.ENGLISH_US: "University of Applied Sciences Munich",
    }
}