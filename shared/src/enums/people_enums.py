from enum import Enum
import re
from typing import Optional

from shared.src.core.logging import get_food_logger
from .language_enums import LanguageEnum
from .faculty_enums import FacultyEnum

logger = get_food_logger(__name__)


class LSFRole(str, Enum):
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
    def from_string(cls, text: str) -> "LSFRole":
        """Extract LSF role from text string"""
        if not text:
            return cls.UNKNOWN
            
        text = text.strip()
        
        # Check translations first
        for role, translations in lsf_role_translations.items():
            if text == translations.get(LanguageEnum.GERMAN, ""):
                return role
                
        logger.warning(f"No matching LSF role found for text: {text}")
        return cls.UNKNOWN

    @classmethod
    def from_id(cls, role_id: int, role_name: str) -> "LSFRole":
        """Create LSFRole from LSF system ID and name"""
        logger.debug(f"Creating LSFRole from ID {role_id} and name: {role_name}")
        return cls.from_string(role_name)


class AcademicTitle(str, Enum):
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
    def from_string(cls, text: str) -> "AcademicTitle":
        """Extract academic title from text string"""
        if not text:
            return cls.UNKNOWN
            
        text = text.strip()
        
        # Check translations first
        for title, translations in academic_title_translations.items():
            if text == translations.get(LanguageEnum.GERMAN, ""):
                return title
        
        # Pattern matching for common variations if not found in translations
        if text.startswith("Prof."):
            if "Dr. Dr." in text:
                return cls.PROF_DR_DR
            elif "Dr. habil." in text:
                return cls.PROF_DR_HABIL
            elif "Dr. h.c." in text:
                return cls.PROF_DR_HC
            elif "em." in text:
                return cls.PROF_EM_DR
            elif "i.R." in text:
                return cls.PROF_IR_DR
            elif "Dr." in text:
                return cls.PROF_DR
            else:
                return cls.PROF_DR
                
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


# Helper function to map CSV faculty names to existing FacultyEnum
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


# Translation dictionaries following the pattern from faculty_enums.py
lsf_role_translations = {
    LSFRole.ABGEORDNETE_LEHRKRAFT: {
        LanguageEnum.GERMAN: "Abgeordnete Lehrkraft",
        LanguageEnum.ENGLISH_US: "Delegated Teaching Staff",
    },
    LSFRole.AKADEMISCHER_DIREKTOR: {
        LanguageEnum.GERMAN: "Akademische/r Direktor/in",
        LanguageEnum.ENGLISH_US: "Academic Director",
    },
    LSFRole.AKADEMISCHER_OBERRAT: {
        LanguageEnum.GERMAN: "Akademische/r Oberrat/Oberrätin",
        LanguageEnum.ENGLISH_US: "Senior Academic Councilor",
    },
    LSFRole.AKADEMISCHER_RAT: {
        LanguageEnum.GERMAN: "Akademische/r Rat/Rätin",
        LanguageEnum.ENGLISH_US: "Academic Councilor",
    },
    LSFRole.APL_PROFESSOR: {
        LanguageEnum.GERMAN: "Apl. Professor/in",
        LanguageEnum.ENGLISH_US: "Associate Professor (apl.)",
    },
    LSFRole.ASSISTENT: {
        LanguageEnum.GERMAN: "Assistent/in",
        LanguageEnum.ENGLISH_US: "Assistant",
    },
    LSFRole.EMERITIERTER_PROFESSOR: {
        LanguageEnum.GERMAN: "Emeritierte/r Professor/in",
        LanguageEnum.ENGLISH_US: "Professor Emeritus",
    },
    LSFRole.EXTERNER_DOZENT: {
        LanguageEnum.GERMAN: "Externe/r Dozent/in",
        LanguageEnum.ENGLISH_US: "External Lecturer",
    },
    LSFRole.GASTPROFESSOR: {
        LanguageEnum.GERMAN: "Gastprofessor/in",
        LanguageEnum.ENGLISH_US: "Visiting Professor",
    },
    LSFRole.HONORARPROFESSOR: {
        LanguageEnum.GERMAN: "Honorarprofessor/in",
        LanguageEnum.ENGLISH_US: "Honorary Professor",
    },
    LSFRole.JUNIORPROFESSOR: {
        LanguageEnum.GERMAN: "Juniorprofessor/in",
        LanguageEnum.ENGLISH_US: "Junior Professor",
    },
    LSFRole.LEHRBEAUFTRAGTER: {
        LanguageEnum.GERMAN: "Lehrbeauftragte/r",
        LanguageEnum.ENGLISH_US: "Lecturer",
    },
    LSFRole.LEHRKRAFT_BESONDERE_AUFGABEN: {
        LanguageEnum.GERMAN: "Lehrkraft für besondere Aufgaben",
        LanguageEnum.ENGLISH_US: "Teaching Staff for Special Tasks",
    },
    LSFRole.LEHRSTUHLVERTRETER: {
        LanguageEnum.GERMAN: "Lehrstuhlvertreter/in",
        LanguageEnum.ENGLISH_US: "Chair Representative",
    },
    LSFRole.LEKTOR: {
        LanguageEnum.GERMAN: "Lektor/in",
        LanguageEnum.ENGLISH_US: "Senior Lecturer",
    },
    LSFRole.LTD_AKADEMISCHER_DIREKTOR: {
        LanguageEnum.GERMAN: "Ltd. Akadmische/r Direktor/in",
        LanguageEnum.ENGLISH_US: "Senior Academic Director",
    },
    LSFRole.PRIVATDOZENT: {
        LanguageEnum.GERMAN: "Privatdozent/in",
        LanguageEnum.ENGLISH_US: "Privatdozent",
    },
    LSFRole.PROFESSOR_IR: {
        LanguageEnum.GERMAN: "Professor i.R.",
        LanguageEnum.ENGLISH_US: "Professor (Retired)",
    },
    LSFRole.PROFESSOR: {
        LanguageEnum.GERMAN: "Professor/in",
        LanguageEnum.ENGLISH_US: "Professor",
    },
    LSFRole.PROFESSURVERTRETER: {
        LanguageEnum.GERMAN: "Professurvertreter/in",
        LanguageEnum.ENGLISH_US: "Professor Representative",
    },
    LSFRole.TUTOR: {
        LanguageEnum.GERMAN: "Tutor/in",
        LanguageEnum.ENGLISH_US: "Tutor",
    },
    LSFRole.UNIVERSITAETSDOZENT: {
        LanguageEnum.GERMAN: "Universitätsdozent/in",
        LanguageEnum.ENGLISH_US: "University Lecturer",
    },
    LSFRole.SONST_DOZENT: {
        LanguageEnum.GERMAN: "sonst. Dozent/in",
        LanguageEnum.ENGLISH_US: "Other Lecturer",
    },
    LSFRole.ASSISTENZARZT: {
        LanguageEnum.GERMAN: "Assistenzarzt/Assistenzärztin",
        LanguageEnum.ENGLISH_US: "Resident Physician",
    },
    LSFRole.CHEFARZT: {
        LanguageEnum.GERMAN: "Chefarzt/Chefärztin",
        LanguageEnum.ENGLISH_US: "Chief Physician",
    },
    LSFRole.OBERARZT: {
        LanguageEnum.GERMAN: "Oberarzt/Oberärztin",
        LanguageEnum.ENGLISH_US: "Senior Physician",
    },
    LSFRole.OBERASSISTENT: {
        LanguageEnum.GERMAN: "Oberassistent/in",
        LanguageEnum.ENGLISH_US: "Senior Assistant",
    },
    LSFRole.WISSENSCHAFTLICHER_MITARBEITER: {
        LanguageEnum.GERMAN: "Wissenschaftliche/r Mitarbeiter/in",
        LanguageEnum.ENGLISH_US: "Research Associate",
    },
    LSFRole.WISSENSCHAFTLICHER_ANGESTELLTER: {
        LanguageEnum.GERMAN: "Wissenschaftliche/r Angestellte/r",
        LanguageEnum.ENGLISH_US: "Scientific Staff",
    },
    LSFRole.WISSENSCHAFTLICHER_ASSISTENT: {
        LanguageEnum.GERMAN: "Wissenschaftliche/r Assistent/in",
        LanguageEnum.ENGLISH_US: "Research Assistant",
    },
    LSFRole.WISSENSCHAFTLICHE_HILFSKRAFT: {
        LanguageEnum.GERMAN: "Wissenschaftliche Hilfskraft",
        LanguageEnum.ENGLISH_US: "Student Research Assistant",
    },
    LSFRole.PROJEKTMITARBEITER: {
        LanguageEnum.GERMAN: "Projektmitarbeiter/in",
        LanguageEnum.ENGLISH_US: "Project Staff",
    },
    LSFRole.GESCHAEFTSFUEHRUNG: {
        LanguageEnum.GERMAN: "Geschäftsführung",
        LanguageEnum.ENGLISH_US: "Management",
    },
    LSFRole.GESCHAEFTSSTELLE: {
        LanguageEnum.GERMAN: "Geschäftsstelle",
        LanguageEnum.ENGLISH_US: "Office",
    },
    LSFRole.MITARBEITER: {
        LanguageEnum.GERMAN: "Mitarbeiter/in",
        LanguageEnum.ENGLISH_US: "Staff Member",
    },
    LSFRole.NICHTWISSENSCHAFTLICHER_MITARBEITER: {
        LanguageEnum.GERMAN: "Nichtwissenschaftliche/r Mitarbeiter/in",
        LanguageEnum.ENGLISH_US: "Non-Academic Staff",
    },
    LSFRole.SEKRETARIAT: {
        LanguageEnum.GERMAN: "Sekretariat",
        LanguageEnum.ENGLISH_US: "Secretariat",
    },
    LSFRole.SONSTIGER_MITARBEITER: {
        LanguageEnum.GERMAN: "Sonstige/r Mitarbeiter/in",
        LanguageEnum.ENGLISH_US: "Other Staff",
    },
    LSFRole.STUDENTISCHER_MITARBEITER: {
        LanguageEnum.GERMAN: "Studentische/r Mitarbeiter/in",
        LanguageEnum.ENGLISH_US: "Student Assistant",
    },
    LSFRole.STUDIENGANGSKOORDINATOR: {
        LanguageEnum.GERMAN: "Studiengangskoordinator/in",
        LanguageEnum.ENGLISH_US: "Program Coordinator",
    },
    LSFRole.STUDIENREFERENT: {
        LanguageEnum.GERMAN: "Studienreferent/in",
        LanguageEnum.ENGLISH_US: "Academic Advisor",
    },
    LSFRole.VERWALTUNGSANGESTELLTER: {
        LanguageEnum.GERMAN: "Verwaltungsangestellter/in",
        LanguageEnum.ENGLISH_US: "Administrative Staff",
    },
    LSFRole.VORSTAND: {
        LanguageEnum.GERMAN: "Vorstand",
        LanguageEnum.ENGLISH_US: "Board",
    },
    LSFRole.GAST: {
        LanguageEnum.GERMAN: "Gast",
        LanguageEnum.ENGLISH_US: "Guest",
    },
    LSFRole.HILFSKRAFT: {
        LanguageEnum.GERMAN: "Hilfskraft",
        LanguageEnum.ENGLISH_US: "Assistant",
    },
    LSFRole.NA: {
        LanguageEnum.GERMAN: "n/a",
        LanguageEnum.ENGLISH_US: "n/a",
    },
}

academic_title_translations = {
    AcademicTitle.PROF_DR: {
        LanguageEnum.GERMAN: "Prof. Dr.",
        LanguageEnum.ENGLISH_US: "Prof. Dr.",
    },
    AcademicTitle.PROF_DR_DR: {
        LanguageEnum.GERMAN: "Prof. Dr. Dr.",
        LanguageEnum.ENGLISH_US: "Prof. Dr. Dr.",
    },
    AcademicTitle.PROF_DR_HABIL: {
        LanguageEnum.GERMAN: "Prof. Dr. habil.",
        LanguageEnum.ENGLISH_US: "Prof. Dr. habil.",
    },
    AcademicTitle.APL_PROF_DR: {
        LanguageEnum.GERMAN: "apl. Prof. Dr.",
        LanguageEnum.ENGLISH_US: "apl. Prof. Dr.",
    },
    AcademicTitle.PD_DR: {
        LanguageEnum.GERMAN: "PD Dr.",
        LanguageEnum.ENGLISH_US: "PD Dr.",
    },
    AcademicTitle.DR_MED: {
        LanguageEnum.GERMAN: "Dr. med.",
        LanguageEnum.ENGLISH_US: "Dr. med.",
    },
    AcademicTitle.DR_PHIL: {
        LanguageEnum.GERMAN: "Dr. phil.",
        LanguageEnum.ENGLISH_US: "Dr. phil.",
    },
    AcademicTitle.DR_RER_NAT: {
        LanguageEnum.GERMAN: "Dr. rer. nat.",
        LanguageEnum.ENGLISH_US: "Dr. rer. nat.",
    },
    AcademicTitle.PHD: {
        LanguageEnum.GERMAN: "Ph.D.",
        LanguageEnum.ENGLISH_US: "Ph.D.",
    },
    AcademicTitle.MA: {
        LanguageEnum.GERMAN: "M.A.",
        LanguageEnum.ENGLISH_US: "M.A.",
    },
    AcademicTitle.MSC: {
        LanguageEnum.GERMAN: "M.Sc.",
        LanguageEnum.ENGLISH_US: "M.Sc.",
    },
    AcademicTitle.BA: {
        LanguageEnum.GERMAN: "B.A.",
        LanguageEnum.ENGLISH_US: "B.A.",
    },
    AcademicTitle.BSC: {
        LanguageEnum.GERMAN: "B.Sc.",
        LanguageEnum.ENGLISH_US: "B.Sc.",
    },
    # Add more translations as needed
} 