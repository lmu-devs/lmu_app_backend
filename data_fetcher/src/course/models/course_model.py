from typing import List, Optional

from pydantic import BaseModel, Field


class Course(BaseModel):
    """Pydantic model for LMU course data"""

    # Basic course information
    # id: Optional[str] = Field(default=None, description="Unique identifier for the course")
    name: Optional[List[str]] = Field(default=None, alias="Name_value", description="Name of the course")
    degree: Optional[List[str]] = Field(
        default=None,
        alias="Degree_of_completion_value",
        description="Degree awarded upon completion",
    )
    language: Optional[List[str]] = Field(
        default=None,
        alias="Language_value",
        description="Primary language of instruction",
    )
    description: Optional[List[str]] = Field(
        default=None, alias="Description_value", description="Brief course description"
    )
    description_long: Optional[List[str]] = Field(
        default=None,
        alias="Description_long_value",
        description="Detailed course description",
    )
    standard_period: Optional[List[str]] = Field(
        default=None,
        alias="standardPeriodOfStudy_value",
        description="Standard duration of studies",
    )
    # course_structure: Optional[List[str]] = Field(default=None, alias="courseStructureAndModules_value", description="Course structure and modules")
    # title: Optional[List[str]] = Field(default=None, description="Title of the course")
    # content: Optional[List[str]] = Field(default=None, description="Content description")
    # link: Optional[str] = Field(default=None, description="Course link identifier")

    # # Course details
    # type_value: Optional[List[str]] = Field(default=None, alias="Type_value", description="Type of the course")
    # degree_completion: Optional[List[str]] = Field(default=None, alias="Degree_of_completion_value", description="Degree awarded upon completion")
    # ects: Optional[List[str]] = Field(default=None, alias="ECTS_value", description="ECTS credits")
    # language: Optional[List[str]] = Field(default=None, alias="Language_value", description="Primary language of instruction")
    # teaching_language: Optional[List[str]] = Field(default=None, alias="teachingLanguage_value", description="Detailed language of instruction information")

    # # Study information
    # form_of_study: Optional[List[str]] = Field(default=None, alias="formOfStudy_value", description="Form of study")
    # start_of_studies: Optional[List[str]] = Field(default=None, alias="Start_of_studies_value", description="When studies can be started")
    # minimum_period: Optional[List[str]] = Field(default=None, alias="minimumPeriodOfStudy_value", description="Minimum study duration")

    # # Admission and requirements
    # admission_modality: Optional[List[str]] = Field(default=None, alias="Admission_modality_value", description="Admission requirements")
    # admission_restriction: Optional[List[str]] = Field(default=None, alias="admissionRestriction1stSemester_value", description="First semester admission restrictions")
    # special_admission_requirements: Optional[List[str]] = Field(default=None, alias="specialAdmissionRequirements_value", description="Special admission requirements")
    # study_orientation_procedure: Optional[List[str]] = Field(default=None, alias="studyOrientationProcedure_value", description="Study orientation procedure")

    # # Course content and structure
    # desired_profile: Optional[List[str]] = Field(default=None, alias="desiredProfile_value", description="Desired student profile")

    # # Career and occupation
    # activity_occupation: Optional[List[str]] = Field(default=None, alias="activityAndOccupation_value", description="Career and occupation possibilities")

    # # Additional information
    # faculty_list: Optional[List[str]] = Field(default=None, alias="facultiesList_value", description="List of associated faculties")
    # contacts_content: Optional[List[str]] = Field(default=None, alias="contactsContent_value", description="Contact information")
    # contacts_facilities: Optional[List[str]] = Field(default=None, alias="contactsFacilities_value", description="Facility contact information")
    # detailpage_link: Optional[List[str]] = Field(default=None, description="Link to detailed course page")

    # # Combinations and requirements
    # combinations: Optional[List[str]] = Field(default=None, alias="combinations_value", description="Possible subject combinations")
    # combinations_school: Optional[List[str]] = Field(default=None, alias="combinationsSchool_value", description="School-specific combinations")
    # combinations_not_in_use: Optional[List[str]] = Field(default=None, alias="combinationsNotInUse_value", description="Deprecated combinations")
    # mandatory_combinations: Optional[List[bool]] = Field(default=None, alias="mandatoryCombinations_value", description="Whether combinations are mandatory")

    # # Flags and indicators
    # teaching_post: Optional[List[bool]] = Field(default=None, alias="Teaching_post_value", description="Whether it's a teaching position")
    # teaching_qualification: Optional[List[bool]] = Field(default=None, alias="teachingQualification_value", description="Teaching qualification status")
    # show_type: Optional[List[bool]] = Field(default=None, alias="showType_value", description="Whether to show type")
    # anchor_links: Optional[List[bool]] = Field(default=None, alias="anchorLinks_value", description="Whether to show anchor links")
    # assessment_process: Optional[List[bool]] = Field(default=None, alias="assessmentProcess_value", description="Assessment process status")
    # no_time_overlap: Optional[List[bool]] = Field(default=None, alias="noTimeOverlap_value", description="Time overlap restrictions")
    # no_minor_subjects: Optional[List[bool]] = Field(default=None, alias="noMinorSubjects_value", description="Minor subject restrictions")

    # # Additional metadata
    # relevance_sort: Optional[str] = Field(default=None, alias="Relevance_A_to_Z_sort", description="Sorting relevance")
    # synonyms_list: Optional[List[str]] = Field(default=None, alias="synonymsList_value", description="List of synonyms")
    # observations: Optional[List[str]] = Field(default=None, alias="observations_value", description="Additional observations")

    class Config:
        populate_by_name = True
        json_encoders = {
            # Add custom encoders if needed
        }
