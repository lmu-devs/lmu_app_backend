from enum import Enum

from .language_enums import LanguageEnum

class FacultyEnum(Enum):
    CATHOLIC_THEOLOGY = (1, "CATHOLIC_THEOLOGY")
    PROTESTANT_THEOLOGY = (2, "PROTESTANT_THEOLOGY")
    LAW = (3, "LAW")
    BUSINESS_ADMIN = (4, "BUSINESS_ADMIN")
    ECONOMICS = (5, "ECONOMICS")
    MEDICINE = (7, "MEDICINE")
    VETERINARY_MEDICINE = (8, "VETERINARY_MEDICINE")
    HISTORY_ARTS = (9, "HISTORY_ARTS")
    PHILOSOPHY = (10, "PHILOSOPHY")
    PSYCHOLOGY_EDUCATION = (11, "PSYCHOLOGY_EDUCATION")
    CULTURE_STUDIES = (12, "CULTURE_STUDIES")
    LANGUAGES_LITERATURE = (13, "LANGUAGES_LITERATURE")
    SOCIAL_SCIENCES = (15, "SOCIAL_SCIENCES")
    MATH_INFO_STATS = (16, "MATH_INFO_STATS")
    PHYSICS = (17, "PHYSICS")
    CHEMISTRY_PHARMACY = (18, "CHEMISTRY_PHARMACY")
    BIOLOGY = (19, "BIOLOGY")
    GEOSCIENCES = (20, "GEOSCIENCES")

    @property
    def id(self):
        return self.value[0]

    @property
    def code(self):
        return self.value[1]


faculty_translations = {
    FacultyEnum.CATHOLIC_THEOLOGY: {
        LanguageEnum.GERMAN: "Katholisch-Theologische Fakultät",
        LanguageEnum.ENGLISH_US: "Catholic Theology",
    },
    FacultyEnum.PROTESTANT_THEOLOGY: {
        LanguageEnum.GERMAN: "Evangelisch-Theologische Fakultät",
        LanguageEnum.ENGLISH_US: "Protestant Theology",
    },
    FacultyEnum.LAW: {
        LanguageEnum.GERMAN: "Juristische Fakultät",
        LanguageEnum.ENGLISH_US: "Faculty of Law",
    },
    FacultyEnum.BUSINESS_ADMIN: {
        LanguageEnum.GERMAN: "Fakultät für Betriebswirtschaft",
        LanguageEnum.ENGLISH_US: "Faculty of Business Administration",
    },
    FacultyEnum.ECONOMICS: {
        LanguageEnum.GERMAN: "Volkswirtschaftliche Fakultät",
        LanguageEnum.ENGLISH_US: "Faculty of Economics",
    },
    FacultyEnum.MEDICINE: {
        LanguageEnum.GERMAN: "Medizinische Fakultät",
        LanguageEnum.ENGLISH_US: "Faculty of Medicine",
    },
    FacultyEnum.VETERINARY_MEDICINE: {
        LanguageEnum.GERMAN: "Tierärztliche Fakultät",
        LanguageEnum.ENGLISH_US: "Faculty of Veterinary Medicine",
    },
    FacultyEnum.HISTORY_ARTS: {
        LanguageEnum.GERMAN: "Fakultät für Geschichts- und Kunstwissenschaften",
        LanguageEnum.ENGLISH_US: "Faculty of History and Art",
    },
    FacultyEnum.PHILOSOPHY: {
        LanguageEnum.GERMAN: "Fakultät für Philosophie, Wissenschaftstheorie und Religionswissenschaft",
        LanguageEnum.ENGLISH_US: "Faculty of Philosophy, Science of Religion and Religious Studies",
    },
    FacultyEnum.PSYCHOLOGY_EDUCATION: {
        LanguageEnum.GERMAN: "Fakultät für Psychologie und Pädagogik",
        LanguageEnum.ENGLISH_US: "Faculty of Psychology and Education",
    },
    FacultyEnum.CULTURE_STUDIES: {
        LanguageEnum.GERMAN: "Fakultät für Kulturwissenschaften",
        LanguageEnum.ENGLISH_US: "Faculty of Culture Studies",
    },
    FacultyEnum.LANGUAGES_LITERATURE: {
        LanguageEnum.GERMAN: "Fakultät für Sprach- und Literaturwissenschaften",
        LanguageEnum.ENGLISH_US: "Faculty of Language and Literature",
    },
    FacultyEnum.SOCIAL_SCIENCES: {
        LanguageEnum.GERMAN: "Sozialwissenschaftliche Fakultät",
        LanguageEnum.ENGLISH_US: "Faculty of Social Sciences",
    },
    FacultyEnum.MATH_INFO_STATS: {
        LanguageEnum.GERMAN: "Fakultät für Mathematik, Informatik und Statistik",
        LanguageEnum.ENGLISH_US: "Faculty of Mathematics, Computer Science and Statistics",
    },
    FacultyEnum.PHYSICS: {
        LanguageEnum.GERMAN: "Fakultät für Physik",
        LanguageEnum.ENGLISH_US: "Faculty of Physics",
    },
    FacultyEnum.CHEMISTRY_PHARMACY: {
        LanguageEnum.GERMAN: "Fakultät für Chemie und Pharmazie",
        LanguageEnum.ENGLISH_US: "Faculty of Chemistry and Pharmacy",
    },
    FacultyEnum.BIOLOGY: {
        LanguageEnum.GERMAN: "Fakultät für Biologie",
        LanguageEnum.ENGLISH_US: "Faculty of Biology",
    },
    FacultyEnum.GEOSCIENCES: {
        LanguageEnum.GERMAN: "Fakultät für Geowissenschaften",
        LanguageEnum.ENGLISH_US: "Faculty of Geosciences",
    },
}
