from enum import Enum
import re
from typing import Optional

from shared.src.core.logging import get_main_fetcher_logger
from .language_enums import LanguageEnum
from .faculty_enums import FacultyEnum

logger = get_main_fetcher_logger(__name__)


class GenderEnum(str, Enum):
    """Gender categories"""
    
    MALE = "MALE"
    FEMALE = "FEMALE"
    DIVERSE = "DIVERSE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, text: str) -> "GenderEnum":
        """Extract gender from text string"""
        if not text:
            return cls.UNKNOWN
            
        text = text.strip().lower()
        
        if text in ["männlich", "male", "m"]:
            return cls.MALE
        elif text in ["weiblich", "female", "f", "w"]:
            return cls.FEMALE
        elif text in ["divers", "diverse", "d"]:
            return cls.DIVERSE
        else:
            return cls.UNKNOWN


class LSFRoleEnum(str, Enum):
    """Actual roles from LMU LSF system"""
    
    # Teaching and Academic Staff
    ABGEORDNETE_LEHRKRAFT = "ABGEORDNETE_LEHRKRAFT"
    AKADEMISCHER_DIREKTOR = "AKADEMISCHER_DIREKTOR"
    AKADEMISCHER_OBERRAT = "AKADEMISCHER_OBERRAT"
    AKADEMISCHER_RAT = "AKADEMISCHER_RAT"
    APL_PROFESSOR = "APL_PROFESSOR"
    ASSISTENT = "ASSISTENT"
    EMERITIERTER_PROFESSOR = "EMERITIERTER_PROFESSOR"
    EXTERNER_DOZENT = "EXTERNER_DOZENT"
    GASTPROFESSOR = "GASTPROFESSOR"
    HONORARPROFESSOR = "HONORARPROFESSOR"
    JUNIORPROFESSOR = "JUNIORPROFESSOR"
    LEHRBEAUFTRAGTER = "LEHRBEAUFTRAGTER"
    LEHRKRAFT_BESONDERE_AUFGABEN = "LEHRKRAFT_BESONDERE_AUFGABEN"
    LEHRSTUHLVERTRETER = "LEHRSTUHLVERTRETER"
    LEKTOR = "LEKTOR"
    LTD_AKADEMISCHER_DIREKTOR = "LTD_AKADEMISCHER_DIREKTOR"
    PRIVATDOZENT = "PRIVATDOZENT"
    PROFESSOR_IR = "PROFESSOR_IR"
    PROFESSOR = "PROFESSOR"
    PROFESSURVERTRETER = "PROFESSURVERTRETER"
    TUTOR = "TUTOR"
    UNIVERSITAETSDOZENT = "UNIVERSITAETSDOZENT"
    SONST_DOZENT = "SONST_DOZENT"
    
    # Medical Staff
    ASSISTENZARZT = "ASSISTENZARZT"
    CHEFARZT = "CHEFARZT"
    OBERARZT = "OBERARZT"
    OBERASSISTENT = "OBERASSISTENT"
    
    # Research and Academic Support
    WISSENSCHAFTLICHER_MITARBEITER = "WISSENSCHAFTLICHER_MITARBEITER"
    WISSENSCHAFTLICHER_ANGESTELLTER = "WISSENSCHAFTLICHER_ANGESTELLTER"
    WISSENSCHAFTLICHER_ASSISTENT = "WISSENSCHAFTLICHER_ASSISTENT"
    WISSENSCHAFTLICHE_HILFSKRAFT = "WISSENSCHAFTLICHE_HILFSKRAFT"
    PROJEKTMITARBEITER = "PROJEKTMITARBEITER"
    
    # Administrative and Support Staff
    GESCHAEFTSFUEHRUNG = "GESCHAEFTSFUEHRUNG"
    GESCHAEFTSSTELLE = "GESCHAEFTSSTELLE"
    MITARBEITER = "MITARBEITER"
    NICHTWISSENSCHAFTLICHER_MITARBEITER = "NICHTWISSENSCHAFTLICHER_MITARBEITER"
    SEKRETARIAT = "SEKRETARIAT"
    SONSTIGER_MITARBEITER = "SONSTIGER_MITARBEITER"
    STUDENTISCHER_MITARBEITER = "STUDENTISCHER_MITARBEITER"
    STUDIENGANGSKOORDINATOR = "STUDIENGANGSKOORDINATOR"
    STUDIENREFERENT = "STUDIENREFERENT"
    VERWALTUNGSANGESTELLTER = "VERWALTUNGSANGESTELLTER"
    VORSTAND = "VORSTAND"
    
    # Other
    GAST = "GAST"
    HILFSKRAFT = "HILFSKRAFT"
    NA = "NA"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, text: str) -> "LSFRoleEnum":
        """Extract LSF role from text string"""
        if not text:
            return cls.UNKNOWN
            
        text = text.strip()
        
        # First, try direct enum value match (for cases like "ASSISTENZARZT")
        try:
            return cls(text)
        except ValueError:
            pass
        
        # Check translations second
        for role, translations in lsf_role_translations.items():
            if text == translations.get(LanguageEnum.GERMAN, ""):
                return role
                
        logger.warning(f"No matching LSF role found for text: {text}")
        return cls.UNKNOWN

    @classmethod
    def from_id(cls, role_id: int, role_name: str) -> "LSFRoleEnum":
        """Create LSFRoleEnum from LSF system ID and name"""
        logger.debug(f"Creating LSFRoleEnum from ID {role_id} and name: {role_name}")
        return cls.from_string(role_name)


class AcademicTitleEnum(str, Enum):
    """Academic titles and degrees from LMU system"""
    
    # Professor titles
    PROF_DR = "PROF_DR"
    PROF_DR_DR = "PROF_DR_DR"
    PROF_DR_HABIL = "PROF_DR_HABIL"
    PROF_DR_HC = "PROF_DR_HC"
    PROF_DR_HC_MULT = "PROF_DR_HC_MULT"
    PROF_EM_DR = "PROF_EM_DR"
    PROF_EM = "PROF_EM"
    PROF_IR_DR = "PROF_IR_DR"
    UNIV_PROF_DR = "UNIV_PROF_DR"
    UNIV_PROF = "UNIV_PROF"
    
    # apl. Professor (außerplanmäßiger Professor)
    APL_PROF_DR = "APL_PROF_DR"
    APL_PROF = "APL_PROF"
    
    # Privatdozent
    PD_DR = "PD_DR"
    PRIV_DOZ_DR = "PRIV_DOZ_DR"
    PRIVATDOZENT_DR = "PRIVATDOZENT_DR"
    
    # Medical specializations
    DR_MED = "DR_MED"
    DR_MED_UNIV = "DR_MED_UNIV"
    DR_MED_VET = "DR_MED_VET"
    DR_MED_DENT = "DR_MED_DENT"
    DR_MED_HABIL = "DR_MED_HABIL"
    
    # Academic doctoral degrees
    DR_PHIL = "DR_PHIL"
    DR_RER_NAT = "DR_RER_NAT"
    DR_RER_POL = "DR_RER_POL"
    DR_THEOL = "DR_THEOL"
    DR_JUR = "DR_JUR"
    DR_IUR = "DR_IUR"
    DR_RER_BIOL_HUM = "DR_RER_BIOL_HUM"
    DR_HABIL = "DR_HABIL"
    DR_ING = "DR_ING"
    
    # Double doctorates
    DR_DR = "DR_DR"
    DR_DR_MED = "DR_DR_MED"
    
    # International degrees
    PHD = "PHD"
    MD = "MD"
    
    # Diplom degrees
    DIPL_PSYCH = "DIPL_PSYCH"
    DIPL_BIOL = "DIPL_BIOL"
    DIPL_ING = "DIPL_ING"
    DIPL_MATH = "DIPL_MATH"
    DIPL_PHYS = "DIPL_PHYS"
    DIPL_CHEM = "DIPL_CHEM"
    DIPL_INF = "DIPL_INF"
    DIPL_KFM = "DIPL_KFM"
    
    # Master degrees
    MA = "MA"
    MSC = "MSC"
    MBA = "MBA"
    MPH = "MPH"
    
    # Bachelor degrees
    BA = "BA"
    BSC = "BSC"
    
    # Academic positions
    AKAD_RAT = "AKAD_RAT"
    AKAD_OBERRAT = "AKAD_OBERRAT"
    AKAD_DIREKTOR = "AKAD_DIREKTOR"
    
    # Special cases
    CAND_MED = "CAND_MED"
    STUDIENRAT = "STUDIENRAT"
    OBERARZT = "OBERARZT"
    ZAHNARZT = "ZAHNARZT"
    
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, text: str) -> "AcademicTitleEnum":
        """Extract academic title from text string"""
        if not text:
            return cls.UNKNOWN
            
        text = text.strip()
        
        # Check translations first
        for title, translations in academic_title_translations.items():
            if text == translations.get(LanguageEnum.GERMAN, ""):
                return title
        
        # Normalize the text first
        normalized_text = text.strip()
        
        # Fallback: direct mapping for common variations
        title_mapping = {
            "Prof. Dr.": cls.PROF_DR,
            "Prof. Dr. Dr.": cls.PROF_DR_DR,
            "Prof. Dr. habil.": cls.PROF_DR_HABIL,
            "Prof. Dr. h.c.": cls.PROF_DR_HC,
            "Prof. em. Dr.": cls.PROF_EM_DR,
            "Prof. i.R. Dr.": cls.PROF_IR_DR,
            "apl. Prof. Dr.": cls.APL_PROF_DR,
            "PD Dr.": cls.PD_DR,
            "Dr. med.": cls.DR_MED,
            "Dr.med.": cls.DR_MED,  # Without space
            "Dr. med. univ.": cls.DR_MED_UNIV,
            "Dr.med.univ.": cls.DR_MED_UNIV,  # Without spaces
            "Dr.med.uni.": cls.DR_MED_UNIV,  # Alternative abbreviation
            "Dr. phil.": cls.DR_PHIL,
            "Dr.phil.": cls.DR_PHIL,  # Without space
            "Dr. rer. nat.": cls.DR_RER_NAT,
            "Dr.rer.nat.": cls.DR_RER_NAT,  # Without spaces
            "Dr. rer. pol.": cls.DR_RER_POL,
            "Dr.rer.pol.": cls.DR_RER_POL,  # Without spaces
            "Dr. theol.": cls.DR_THEOL,
            "Dr.theol.": cls.DR_THEOL,  # Without space
            "Dr. jur.": cls.DR_JUR,
            "Dr.jur.": cls.DR_JUR,  # Without space
            "Dr. iur.": cls.DR_IUR,
            "Dr.iur.": cls.DR_IUR,  # Without space
            "Dr. rer. biol. hum.": cls.DR_RER_BIOL_HUM,
            "Dr. habil.": cls.DR_HABIL,
            "Dr.habil.": cls.DR_HABIL,  # Without space
            "Dr. Ing.": cls.DR_ING,
            "Dr.Ing.": cls.DR_ING,  # Without space
            "Dr. Dr.": cls.DR_DR,
            "Dr.Dr.": cls.DR_DR,  # Without space
            "Dr. Dr. med.": cls.DR_DR_MED,
            "Dr.Dr.med.": cls.DR_DR_MED,  # Without spaces
            "Ph.D.": cls.PHD,
            "PhD": cls.PHD,  # Without periods
            "M.D.": cls.MD,
            "MD": cls.MD,  # Without periods
            "M.A.": cls.MA,
            "MA": cls.MA,  # Without periods
            "M.Sc.": cls.MSC,
            "MSc": cls.MSC,  # Without periods
            "M.B.A.": cls.MBA,
            "MBA": cls.MBA,  # Without periods
            "M.P.H.": cls.MPH,
            "MPH": cls.MPH,  # Without periods
            "B.A.": cls.BA,
            "BA": cls.BA,  # Without periods
            "B.Sc.": cls.BSC,
            "BSc": cls.BSC,  # Without periods
            "Dipl.-Psych.": cls.DIPL_PSYCH,
            "Dipl.-Biol.": cls.DIPL_BIOL,
            "Dipl.-Ing.": cls.DIPL_ING,
            "Dipl.-Math.": cls.DIPL_MATH,
            "Dipl.-Phys.": cls.DIPL_PHYS,
            "Dipl.-Chem.": cls.DIPL_CHEM,
            "Dipl.-Inf.": cls.DIPL_INF,
            "Dipl.-Kfm.": cls.DIPL_KFM,
        }
        
        # Try exact match first
        if normalized_text in title_mapping:
            return title_mapping[normalized_text]
        
        # Try pattern matching for complex titles
        if "Dr.med." in normalized_text or "Dr. med." in normalized_text:
            return cls.DR_MED
        elif "Dr.phil." in normalized_text or "Dr. phil." in normalized_text:
            return cls.DR_PHIL
        elif "Dr.rer.nat." in normalized_text or "Dr. rer. nat." in normalized_text:
            return cls.DR_RER_NAT
        elif "Prof." in normalized_text and "Dr." in normalized_text:
            return cls.PROF_DR
        elif "Dr." in normalized_text:
            return cls.DR_MED  # Default fallback for Dr. titles
        
        logger.warning(f"No matching academic title found for text: {text}")
        return cls.UNKNOWN


class EmploymentStatusEnum(str, Enum):
    """Employment status categories"""
    
    EXTERN = "EXTERN"
    INTERN = "INTERN"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def from_string(cls, text: str) -> "EmploymentStatusEnum":
        """Extract employment status from text string"""
        if not text:
            return cls.UNKNOWN
            
        text = text.strip().lower()
        
        if text == "extern":
            return cls.EXTERN
        elif text == "intern":
            return cls.INTERN
        else:
            return cls.UNKNOWN


def map_faculty_name_to_enum(german_faculty_name: str) -> FacultyEnum:
    """Map German faculty name from CSV to existing FacultyEnum"""
    if not german_faculty_name:
        return None
        
    faculty_name_mapping = {
        "Evangelisch-Theologische Fakultät": FacultyEnum.PROTESTANT_THEOLOGY,
        "Fakultät für Betriebswirtschaft": FacultyEnum.BUSINESS_ADMIN,
        "Fakultät für Biologie": FacultyEnum.BIOLOGY,
        "Fakultät für Chemie und Pharmazie": FacultyEnum.CHEMISTRY_PHARMACY,
        "Fakultät für Geowissenschaften": FacultyEnum.GEOSCIENCES,
        "Fakultät für Geschichts- und Kunstwissenschaften": FacultyEnum.HISTORY_ARTS,
        "Fakultät für Kulturwissenschaften": FacultyEnum.CULTURE_STUDIES,
        "Fakultät für Mathematik, Informatik und Statistik": FacultyEnum.MATH_INFO_STATS,
        "Fakultät für Philosophie, Wissenschaftstheorie und Religionswissenschaft": FacultyEnum.PHILOSOPHY,
        "Fakultät für Physik": FacultyEnum.PHYSICS,
        "Fakultät für Psychologie und Pädagogik": FacultyEnum.PSYCHOLOGY_EDUCATION,
        "Fakultät für Sprach- und Literaturwissenschaften": FacultyEnum.LANGUAGES_LITERATURE,
        "Fakultätsübergreifende Einrichtungen": None,  # Special case - not a faculty
        "Juristische Fakultät": FacultyEnum.LAW,
        "Katholisch-Theologische Fakultät": FacultyEnum.CATHOLIC_THEOLOGY,
        "Medizinische Fakultät": FacultyEnum.MEDICINE,
        "Sozialwissenschaftliche Fakultät": FacultyEnum.SOCIAL_SCIENCES,
        "Tierärztliche Fakultät": FacultyEnum.VETERINARY_MEDICINE,
        "Volkswirtschaftliche Fakultät": FacultyEnum.ECONOMICS,
    }
    
    return faculty_name_mapping.get(german_faculty_name.strip())


def map_academic_title_to_enum(academic_title_text: str) -> AcademicTitleEnum:
    """Map academic title text to AcademicTitleEnum"""
    if not academic_title_text:
        return None
        
    # First try to match using the from_string method
    try:
        return AcademicTitleEnum.from_string(academic_title_text)
    except Exception:
        pass
    
    # Normalize the text first
    normalized_text = academic_title_text.strip()
    
    # Fallback: direct mapping for common variations
    title_mapping = {
        "Prof. Dr.": AcademicTitleEnum.PROF_DR,
        "Prof. Dr. Dr.": AcademicTitleEnum.PROF_DR_DR,
        "Prof. Dr. habil.": AcademicTitleEnum.PROF_DR_HABIL,
        "Prof. Dr. h.c.": AcademicTitleEnum.PROF_DR_HC,
        "Prof. em. Dr.": AcademicTitleEnum.PROF_EM_DR,
        "Prof. i.R. Dr.": AcademicTitleEnum.PROF_IR_DR,
        "apl. Prof. Dr.": AcademicTitleEnum.APL_PROF_DR,
        "PD Dr.": AcademicTitleEnum.PD_DR,
        "Dr. med.": AcademicTitleEnum.DR_MED,
        "Dr.med.": AcademicTitleEnum.DR_MED,  # Without space
        "Dr. med. univ.": AcademicTitleEnum.DR_MED_UNIV,
        "Dr.med.univ.": AcademicTitleEnum.DR_MED_UNIV,  # Without spaces
        "Dr.med.uni.": AcademicTitleEnum.DR_MED_UNIV,  # Alternative abbreviation
        "Dr. phil.": AcademicTitleEnum.DR_PHIL,
        "Dr.phil.": AcademicTitleEnum.DR_PHIL,  # Without space
        "Dr. rer. nat.": AcademicTitleEnum.DR_RER_NAT,
        "Dr.rer.nat.": AcademicTitleEnum.DR_RER_NAT,  # Without spaces
        "Dr. rer. pol.": AcademicTitleEnum.DR_RER_POL,
        "Dr.rer.pol.": AcademicTitleEnum.DR_RER_POL,  # Without spaces
        "Dr. theol.": AcademicTitleEnum.DR_THEOL,
        "Dr.theol.": AcademicTitleEnum.DR_THEOL,  # Without space
        "Dr. jur.": AcademicTitleEnum.DR_JUR,
        "Dr.jur.": AcademicTitleEnum.DR_JUR,  # Without space
        "Dr. iur.": AcademicTitleEnum.DR_IUR,
        "Dr.iur.": AcademicTitleEnum.DR_IUR,  # Without space
        "Dr. rer. biol. hum.": AcademicTitleEnum.DR_RER_BIOL_HUM,
        "Dr. habil.": AcademicTitleEnum.DR_HABIL,
        "Dr.habil.": AcademicTitleEnum.DR_HABIL,  # Without space
        "Dr. Ing.": AcademicTitleEnum.DR_ING,
        "Dr.Ing.": AcademicTitleEnum.DR_ING,  # Without space
        "Dr. Dr.": AcademicTitleEnum.DR_DR,
        "Dr.Dr.": AcademicTitleEnum.DR_DR,  # Without space
        "Dr. Dr. med.": AcademicTitleEnum.DR_DR_MED,
        "Dr.Dr.med.": AcademicTitleEnum.DR_DR_MED,  # Without spaces
        "Ph.D.": AcademicTitleEnum.PHD,
        "PhD": AcademicTitleEnum.PHD,  # Without periods
        "M.D.": AcademicTitleEnum.MD,
        "MD": AcademicTitleEnum.MD,  # Without periods
        "M.A.": AcademicTitleEnum.MA,
        "MA": AcademicTitleEnum.MA,  # Without periods
        "M.Sc.": AcademicTitleEnum.MSC,
        "MSc": AcademicTitleEnum.MSC,  # Without periods
        "M.B.A.": AcademicTitleEnum.MBA,
        "MBA": AcademicTitleEnum.MBA,  # Without periods
        "M.P.H.": AcademicTitleEnum.MPH,
        "MPH": AcademicTitleEnum.MPH,  # Without periods
        "B.A.": AcademicTitleEnum.BA,
        "BA": AcademicTitleEnum.BA,  # Without periods
        "B.Sc.": AcademicTitleEnum.BSC,
        "BSc": AcademicTitleEnum.BSC,  # Without periods
        "Dipl.-Psych.": AcademicTitleEnum.DIPL_PSYCH,
        "Dipl.-Biol.": AcademicTitleEnum.DIPL_BIOL,
        "Dipl.-Ing.": AcademicTitleEnum.DIPL_ING,
        "Dipl.-Math.": AcademicTitleEnum.DIPL_MATH,
        "Dipl.-Phys.": AcademicTitleEnum.DIPL_PHYS,
        "Dipl.-Chem.": AcademicTitleEnum.DIPL_CHEM,
        "Dipl.-Inf.": AcademicTitleEnum.DIPL_INF,
        "Dipl.-Kfm.": AcademicTitleEnum.DIPL_KFM,
    }
    
    # Try exact match first
    if normalized_text in title_mapping:
        return title_mapping[normalized_text]
    
    # Try pattern matching for complex titles
    if "Dr.med." in normalized_text or "Dr. med." in normalized_text:
        return AcademicTitleEnum.DR_MED
    elif "Dr.phil." in normalized_text or "Dr. phil." in normalized_text:
        return AcademicTitleEnum.DR_PHIL
    elif "Dr.rer.nat." in normalized_text or "Dr. rer. nat." in normalized_text:
        return AcademicTitleEnum.DR_RER_NAT
    elif "Prof." in normalized_text and "Dr." in normalized_text:
        return AcademicTitleEnum.PROF_DR
    elif "Dr." in normalized_text:
        return AcademicTitleEnum.DR_MED  # Default fallback for Dr. titles
    
    return AcademicTitleEnum.UNKNOWN


def map_gender_to_enum(gender_text: str) -> GenderEnum:
    """Map gender text to GenderEnum"""
    if not gender_text:
        return None
        
    return GenderEnum.from_string(gender_text)


def map_employment_status_to_enum(status_text: str) -> EmploymentStatusEnum:
    """Map employment status text to EmploymentStatusEnum"""
    if not status_text:
        return None
        
    # Normalize the text first
    normalized_text = status_text.strip().lower()
    
    # Direct mapping for simple cases
    if normalized_text == "extern":
        return EmploymentStatusEnum.EXTERN
    elif normalized_text == "intern":
        return EmploymentStatusEnum.INTERN
    
    # Smart mapping based on job roles
    # External roles (typically temporary, guest, or non-university positions)
    external_indicators = [
        "gast",  # Guest
        "externe",  # External
        "lehrbeauftragte",  # Lecturer (often external)
        "honorarprofessor",  # Honorary professor (external)
        "gastprofessor",  # Visiting professor (external)
        "privatdozent"  # Private lecturer (often external)
    ]
    
    # Internal roles (typically permanent university staff)
    internal_indicators = [
        "wissenschaftliche",  # Research staff
        "professor",  # Professor
        "akademische",  # Academic staff
        "mitarbeiter",  # Staff member
        "direktor",  # Director
        "oberrat",  # Senior councilor
        "assistent",  # Assistant
        "sekretariat",  # Secretariat
        "verwaltung",  # Administration
        "vorstand",  # Board
        "geschäftsführung",  # Management
        "tutor",  # Tutor
        "hilfskraft"  # Student assistant
    ]
    
    # Check for external indicators
    for indicator in external_indicators:
        if indicator in normalized_text:
            return EmploymentStatusEnum.EXTERN
    
    # Check for internal indicators
    for indicator in internal_indicators:
        if indicator in normalized_text:
            return EmploymentStatusEnum.INTERN
    
    # Default fallback
    return EmploymentStatusEnum.UNKNOWN


def map_lsf_role_to_enum(role_text: str) -> LSFRoleEnum:
    """Map LSF role text to LSFRoleEnum"""
    if not role_text:
        return None
    
    # Normalize the text
    normalized_text = role_text.strip()
    
    # Try direct enum value first
    try:
        return LSFRoleEnum(normalized_text)
    except ValueError:
        pass
    
    # Try the from_string method (which handles translations)
    return LSFRoleEnum.from_string(normalized_text)


# Translation dictionaries following the pattern from faculty_enums.py
lsf_role_translations = {
    LSFRoleEnum.ABGEORDNETE_LEHRKRAFT: {
        LanguageEnum.GERMAN: "Abgeordnete Lehrkraft",
        LanguageEnum.ENGLISH_US: "Delegated Teaching Staff",
    },
    LSFRoleEnum.AKADEMISCHER_DIREKTOR: {
        LanguageEnum.GERMAN: "Akademische/r Direktor/in",
        LanguageEnum.ENGLISH_US: "Academic Director",
    },
    LSFRoleEnum.AKADEMISCHER_OBERRAT: {
        LanguageEnum.GERMAN: "Akademische/r Oberrat/Oberrätin",
        LanguageEnum.ENGLISH_US: "Senior Academic Councilor",
    },
    LSFRoleEnum.AKADEMISCHER_RAT: {
        LanguageEnum.GERMAN: "Akademische/r Rat/Rätin",
        LanguageEnum.ENGLISH_US: "Academic Councilor",
    },
    LSFRoleEnum.APL_PROFESSOR: {
        LanguageEnum.GERMAN: "Apl. Professor/in",
        LanguageEnum.ENGLISH_US: "Associate Professor (apl.)",
    },
    LSFRoleEnum.ASSISTENT: {
        LanguageEnum.GERMAN: "Assistent/in",
        LanguageEnum.ENGLISH_US: "Assistant",
    },
    LSFRoleEnum.EMERITIERTER_PROFESSOR: {
        LanguageEnum.GERMAN: "Emeritierte/r Professor/in",
        LanguageEnum.ENGLISH_US: "Professor Emeritus",
    },
    LSFRoleEnum.EXTERNER_DOZENT: {
        LanguageEnum.GERMAN: "Externe/r Dozent/in",
        LanguageEnum.ENGLISH_US: "External Lecturer",
    },
    LSFRoleEnum.GASTPROFESSOR: {
        LanguageEnum.GERMAN: "Gastprofessor/in",
        LanguageEnum.ENGLISH_US: "Visiting Professor",
    },
    LSFRoleEnum.HONORARPROFESSOR: {
        LanguageEnum.GERMAN: "Honorarprofessor/in",
        LanguageEnum.ENGLISH_US: "Honorary Professor",
    },
    LSFRoleEnum.JUNIORPROFESSOR: {
        LanguageEnum.GERMAN: "Juniorprofessor/in",
        LanguageEnum.ENGLISH_US: "Junior Professor",
    },
    LSFRoleEnum.LEHRBEAUFTRAGTER: {
        LanguageEnum.GERMAN: "Lehrbeauftragte/r",
        LanguageEnum.ENGLISH_US: "Lecturer",
    },
    LSFRoleEnum.LEHRKRAFT_BESONDERE_AUFGABEN: {
        LanguageEnum.GERMAN: "Lehrkraft für besondere Aufgaben",
        LanguageEnum.ENGLISH_US: "Teaching Staff for Special Tasks",
    },
    LSFRoleEnum.LEHRSTUHLVERTRETER: {
        LanguageEnum.GERMAN: "Lehrstuhlvertreter/in",
        LanguageEnum.ENGLISH_US: "Chair Representative",
    },
    LSFRoleEnum.LEKTOR: {
        LanguageEnum.GERMAN: "Lektor/in",
        LanguageEnum.ENGLISH_US: "Senior Lecturer",
    },
    LSFRoleEnum.LTD_AKADEMISCHER_DIREKTOR: {
        LanguageEnum.GERMAN: "Ltd. Akadmische/r Direktor/in",
        LanguageEnum.ENGLISH_US: "Senior Academic Director",
    },
    LSFRoleEnum.PRIVATDOZENT: {
        LanguageEnum.GERMAN: "Privatdozent/in",
        LanguageEnum.ENGLISH_US: "Privatdozent",
    },
    LSFRoleEnum.PROFESSOR_IR: {
        LanguageEnum.GERMAN: "Professor i.R.",
        LanguageEnum.ENGLISH_US: "Professor (Retired)",
    },
    LSFRoleEnum.PROFESSOR: {
        LanguageEnum.GERMAN: "Professor/in",
        LanguageEnum.ENGLISH_US: "Professor",
    },
    LSFRoleEnum.PROFESSURVERTRETER: {
        LanguageEnum.GERMAN: "Professurvertreter/in",
        LanguageEnum.ENGLISH_US: "Professor Representative",
    },
    LSFRoleEnum.TUTOR: {
        LanguageEnum.GERMAN: "Tutor/in",
        LanguageEnum.ENGLISH_US: "Tutor",
    },
    LSFRoleEnum.UNIVERSITAETSDOZENT: {
        LanguageEnum.GERMAN: "Universitätsdozent/in",
        LanguageEnum.ENGLISH_US: "University Lecturer",
    },
    LSFRoleEnum.SONST_DOZENT: {
        LanguageEnum.GERMAN: "sonst. Dozent/in",
        LanguageEnum.ENGLISH_US: "Other Lecturer",
    },
    LSFRoleEnum.ASSISTENZARZT: {
        LanguageEnum.GERMAN: "Assistenzarzt/Assistenzärztin",
        LanguageEnum.ENGLISH_US: "Resident Physician",
    },
    LSFRoleEnum.CHEFARZT: {
        LanguageEnum.GERMAN: "Chefarzt/Chefärztin",
        LanguageEnum.ENGLISH_US: "Chief Physician",
    },
    LSFRoleEnum.OBERARZT: {
        LanguageEnum.GERMAN: "Oberarzt/Oberärztin",
        LanguageEnum.ENGLISH_US: "Senior Physician",
    },
    LSFRoleEnum.OBERASSISTENT: {
        LanguageEnum.GERMAN: "Oberassistent/in",
        LanguageEnum.ENGLISH_US: "Senior Assistant",
    },
    LSFRoleEnum.WISSENSCHAFTLICHER_MITARBEITER: {
        LanguageEnum.GERMAN: "Wissenschaftliche/r Mitarbeiter/in",
        LanguageEnum.ENGLISH_US: "Research Associate",
    },
    LSFRoleEnum.WISSENSCHAFTLICHER_ANGESTELLTER: {
        LanguageEnum.GERMAN: "Wissenschaftliche/r Angestellte/r",
        LanguageEnum.ENGLISH_US: "Scientific Staff",
    },
    LSFRoleEnum.WISSENSCHAFTLICHER_ASSISTENT: {
        LanguageEnum.GERMAN: "Wissenschaftliche/r Assistent/in",
        LanguageEnum.ENGLISH_US: "Research Assistant",
    },
    LSFRoleEnum.WISSENSCHAFTLICHE_HILFSKRAFT: {
        LanguageEnum.GERMAN: "Wissenschaftliche Hilfskraft",
        LanguageEnum.ENGLISH_US: "Student Research Assistant",
    },
    LSFRoleEnum.PROJEKTMITARBEITER: {
        LanguageEnum.GERMAN: "Projektmitarbeiter/in",
        LanguageEnum.ENGLISH_US: "Project Staff",
    },
    LSFRoleEnum.GESCHAEFTSFUEHRUNG: {
        LanguageEnum.GERMAN: "Geschäftsführung",
        LanguageEnum.ENGLISH_US: "Management",
    },
    LSFRoleEnum.GESCHAEFTSSTELLE: {
        LanguageEnum.GERMAN: "Geschäftsstelle",
        LanguageEnum.ENGLISH_US: "Office",
    },
    LSFRoleEnum.MITARBEITER: {
        LanguageEnum.GERMAN: "Mitarbeiter/in",
        LanguageEnum.ENGLISH_US: "Staff Member",
    },
    LSFRoleEnum.NICHTWISSENSCHAFTLICHER_MITARBEITER: {
        LanguageEnum.GERMAN: "Nichtwissenschaftliche/r Mitarbeiter/in",
        LanguageEnum.ENGLISH_US: "Non-Academic Staff",
    },
    LSFRoleEnum.SEKRETARIAT: {
        LanguageEnum.GERMAN: "Sekretariat",
        LanguageEnum.ENGLISH_US: "Secretariat",
    },
    LSFRoleEnum.SONSTIGER_MITARBEITER: {
        LanguageEnum.GERMAN: "Sonstige/r Mitarbeiter/in",
        LanguageEnum.ENGLISH_US: "Other Staff",
    },
    LSFRoleEnum.STUDENTISCHER_MITARBEITER: {
        LanguageEnum.GERMAN: "Studentische/r Mitarbeiter/in",
        LanguageEnum.ENGLISH_US: "Student Assistant",
    },
    LSFRoleEnum.STUDIENGANGSKOORDINATOR: {
        LanguageEnum.GERMAN: "Studiengangskoordinator/in",
        LanguageEnum.ENGLISH_US: "Program Coordinator",
    },
    LSFRoleEnum.STUDIENREFERENT: {
        LanguageEnum.GERMAN: "Studienreferent/in",
        LanguageEnum.ENGLISH_US: "Academic Advisor",
    },
    LSFRoleEnum.VERWALTUNGSANGESTELLTER: {
        LanguageEnum.GERMAN: "Verwaltungsangestellter/in",
        LanguageEnum.ENGLISH_US: "Administrative Staff",
    },
    LSFRoleEnum.VORSTAND: {
        LanguageEnum.GERMAN: "Vorstand",
        LanguageEnum.ENGLISH_US: "Board",
    },
    LSFRoleEnum.GAST: {
        LanguageEnum.GERMAN: "Gast",
        LanguageEnum.ENGLISH_US: "Guest",
    },
    LSFRoleEnum.HILFSKRAFT: {
        LanguageEnum.GERMAN: "Hilfskraft",
        LanguageEnum.ENGLISH_US: "Assistant",
    },
    LSFRoleEnum.NA: {
        LanguageEnum.GERMAN: "n/a",
        LanguageEnum.ENGLISH_US: "n/a",
    },
}

academic_title_translations = {
    AcademicTitleEnum.PROF_DR: {
        LanguageEnum.GERMAN: "Prof. Dr.",
        LanguageEnum.ENGLISH_US: "Prof. Dr.",
    },
    AcademicTitleEnum.PROF_DR_DR: {
        LanguageEnum.GERMAN: "Prof. Dr. Dr.",
        LanguageEnum.ENGLISH_US: "Prof. Dr. Dr.",
    },
    AcademicTitleEnum.PROF_DR_HABIL: {
        LanguageEnum.GERMAN: "Prof. Dr. habil.",
        LanguageEnum.ENGLISH_US: "Prof. Dr. habil.",
    },
    AcademicTitleEnum.APL_PROF_DR: {
        LanguageEnum.GERMAN: "apl. Prof. Dr.",
        LanguageEnum.ENGLISH_US: "apl. Prof. Dr.",
    },
    AcademicTitleEnum.PD_DR: {
        LanguageEnum.GERMAN: "PD Dr.",
        LanguageEnum.ENGLISH_US: "PD Dr.",
    },
    AcademicTitleEnum.DR_MED: {
        LanguageEnum.GERMAN: "Dr. med.",
        LanguageEnum.ENGLISH_US: "Dr. med.",
    },
    AcademicTitleEnum.DR_PHIL: {
        LanguageEnum.GERMAN: "Dr. phil.",
        LanguageEnum.ENGLISH_US: "Dr. phil.",
    },
    AcademicTitleEnum.DR_RER_NAT: {
        LanguageEnum.GERMAN: "Dr. rer. nat.",
        LanguageEnum.ENGLISH_US: "Dr. rer. nat.",
    },
    AcademicTitleEnum.PHD: {
        LanguageEnum.GERMAN: "Ph.D.",
        LanguageEnum.ENGLISH_US: "Ph.D.",
    },
    AcademicTitleEnum.MA: {
        LanguageEnum.GERMAN: "M.A.",
        LanguageEnum.ENGLISH_US: "M.A.",
    },
    AcademicTitleEnum.MSC: {
        LanguageEnum.GERMAN: "M.Sc.",
        LanguageEnum.ENGLISH_US: "M.Sc.",
    },
    AcademicTitleEnum.BA: {
        LanguageEnum.GERMAN: "B.A.",
        LanguageEnum.ENGLISH_US: "B.A.",
    },
    AcademicTitleEnum.BSC: {
        LanguageEnum.GERMAN: "B.Sc.",
        LanguageEnum.ENGLISH_US: "B.Sc.",
    },
    # Add more translations as needed
} 