import re
from datetime import time, date as Date
from pydantic import BaseModel, Field
from typing import Any, List, Tuple, Optional
from pathlib import Path

from shared.src.tables.lectures import (
    LectureTable, PersonTable, InstitutionTable,
    AssociatedTutorialTable, AssociatedClassTable,
    AssociatedProgramTable, AssociatedExamTable,
    ClassBaseInfoTable, ClassSessionTable,
    TreePathTable, ClassMaterialTable,
    ExamInformationTable, EnrollmentDeadlineTable,
    AdditionInformationTable
)

from shared.src.enums.weekday_enum import WeekdayEnum
from shared.src.enums.classes_enum import LectureStartTypeEnum
from shared.src.services.directus_service import DirectusService



class Person(BaseModel):
    first_name: str
    surname: str
    title: Optional[str]

    @classmethod
    def from_str(cls, person: str) -> "Person":
        """Create a Person instance from a string representation."""
        parts = person.split(",")

        if len(parts) == 2:
            surname = parts[0].strip()
            first_name = parts[1].strip()
            return cls(first_name=first_name, surname=surname, title=None)
        if len(parts) >= 3:
            surname = parts[0].removeprefix(parts[2]).strip()
            first_name = parts[1].strip()
            title = parts[2].strip()
            return cls(first_name=first_name, surname=surname, title=title)

        raise RuntimeError("Invalid string to create person")

    def to_table(self) -> PersonTable:
        return PersonTable(
            first_name=self.first_name,
            surname=self.surname,
            title=self.title
        )



class Institution(BaseModel):
    name: str

    def to_table(self) -> InstitutionTable:
        return InstitutionTable(name=self.name)


class PathElement(BaseModel):
    value: str
    index: int


class TreePath(BaseModel):
    path_elements: List[PathElement]

    @classmethod
    def from_list(cls, raw: list[str]) -> "TreePath":
        """Create a TreePath instance from a list of strings."""
        path_elements: List[PathElement] = []

        for i, v in enumerate(raw):
            path_elements += [PathElement(value=v, index=i)]

        return cls(path_elements=path_elements)

    def to_table(self) -> TreePathTable:
        return TreePathTable(path=[pe.value for pe in self.path_elements])


class AssociatedProgram(BaseModel):
    program_name: Optional[str]
    module_classification: Optional[str]
    ects: Optional[int]
    degree: Optional[str]

    def to_table(self) -> AssociatedProgramTable:
        return AssociatedProgramTable(
            program_name=self.program_name,
            module_classification=self.module_classification,
            ects=self.ects,
            degree=self.degree
        )


class ClassBaseInfo(BaseModel):
    institutions: Optional[list[Institution]]
    class_type: Optional[str] = Field(alias="Veranstaltungsart", default=None)
    class_id: Optional[str] = Field(alias="Veranstaltungsnummer", default=None)
    class_cycle: Optional[str] = Field(alias="Rhythmus", default=None)
    semester: Optional[str] = Field(alias="Semester", default=None)
    sws: Optional[float] = Field(alias="SWS", default=None)
    max_participants: Optional[int] = Field(alias="Max. Teilnehmer/-innen", default=None)
    in_person_type: Optional[str] = Field(alias="Veranstaltungstyp", default=None)
    language: Optional[str] = Field(alias="Sprache", default=None)
    for_exchange_students: Optional[str] = Field(alias="für Austauschstudierende", default=None)
    links: Optional[str] = Field(alias="Weitere Links", default=None)
    sigel: Optional[str] = Field(alias="Sigel", default=None)

    def to_table(self) -> ClassBaseInfoTable:
        return ClassBaseInfoTable(
            class_type=self.class_type,
            class_id=self.class_id,
            class_cycle=self.class_cycle,
            semester=self.semester,
            sws=self.sws,
            max_participants=self.max_participants,
            in_person_type=self.in_person_type,
            language=self.language,
            for_exchange_students=self.for_exchange_students,
            links=self.links,
            sigel=self.sigel
        )


class ClassSession(BaseModel):
    caption: Optional[str]
    weekday: Optional[WeekdayEnum]
    starting_time: Optional[time]
    ending_time: Optional[time]
    timing_type: Optional[LectureStartTypeEnum]
    rythm: Optional[str]
    duration_start: Optional[Date]
    duration_end: Optional[Date]
    room: Optional[str]
    lecturer: Optional[str]
    remark: Optional[str]
    cancelled_dates: Optional[str]

    def to_table(self) -> ClassSessionTable:
        return ClassSessionTable(
            caption=self.caption,
            weekday=self.weekday,
            starting_time=self.starting_time,
            ending_time=self.ending_time,
            timing_type=self.timing_type,
            rythm=self.rythm,
            duration_start=self.duration_start,
            duration_end=self.duration_end,
            room=self.room,
            lecturer=self.lecturer,
            remark=self.remark,
            cancelled_dates=self.cancelled_dates
        )


class ClassMaterial(BaseModel):
    valid_from: Optional[Date]
    valid_to: Optional[Date]
    file_name: Optional[str]
    description: Optional[str]

    def to_table(self) -> ClassMaterialTable:
        return ClassMaterialTable(
            valid_from=self.valid_from,
            valid_to=self.valid_to,
            file_name=self.file_name,
            description=self.description
        )


class AssociatedExam(BaseModel):
    module_name: Optional[str]
    program_name: Optional[str]
    ects: Optional[int]
    module_classification: Optional[str]
    degree: Optional[str]
    module_id: Optional[str]
    exam_id: Optional[str]
    po_version: Optional[str]

    def to_table(self) -> AssociatedExamTable:
        return AssociatedExamTable(
            module_name=self.module_name,
            program_name=self.program_name,
            ects=self.ects,
            module_classification=self.module_classification,
            degree=self.degree,
            module_id=self.module_id,
            exam_id=self.exam_id,
            po_version=self.po_version
        )

class AdditionInformation(BaseModel):
    remark: Optional[str] = Field(default=None, alias="Bemerkung")
    literature: Optional[str] = Field(default=None, alias="Literatur")
    date: Optional[str] = Field(default=None, alias="Datum")
    registration: Optional[str] = Field(default=None, alias="Anmeldung")
    format: Optional[str] = Field(default=None, alias="Form")
    content: Optional[str] = Field(default=None, alias="Inhalt")
    learning_content: Optional[str] = Field(default=None, alias="Lerninhalte")
    target_group: Optional[str] = Field(default=None, alias="Zielgruppe")
    location: Optional[str] = Field(default=None, alias="Ort")
    comment: Optional[str] = Field(default=None, alias="Kommentar")
    assessment: Optional[str] = Field(default=None, alias="Leistungsnachweis")
    time: Optional[str] = Field(default=None, alias="Uhrzeit")
    topic: Optional[str] = Field(default=None, alias="Thema")
    short_comment: Optional[str] = Field(default=None, alias="Kurzkommentar")
    prerequisites: Optional[str] = Field(default=None, alias="Voraussetzungen")
    number: Optional[str] = Field(default=None, alias="Nr.")
    type: Optional[str] = Field(default=None, alias="Typ")

    def to_table(self) -> AdditionInformationTable:
        return AdditionInformationTable(
            remark=self.remark,
            literature=self.literature,
            date=self.date,
            registration=self.registration,
            format=self.format,
            content=self.content,
            learning_content=self.learning_content,
            target_group=self.target_group,
            location=self.location,
            comment=self.comment,
            assessment=self.assessment,
            time=self.time,
            topic=self.topic,
            short_comment=self.short_comment,
            prerequisites=self.prerequisites,
            number=self.number,
            type=self.type
        )

class ExamInformation(BaseModel):
    ects: Optional[int] = Field(None, alias="ECTS")
    examiner: Optional[str] = Field(None, alias="Prüfer/-in")
    degree_program: Optional[str] = Field(None, alias="Studiengang")
    kzfa: Optional[str] = Field(None, alias="KzFa")
    registration_start: Optional[Date] = Field(None)
    registration_end: Optional[Date] = Field(None)
    exam_id: Optional[str] = Field(None, alias="Prüfungsnummer")
    program_version: Optional[str] = Field(None, alias="Pversion")
    degree_awarded: Optional[str] = Field(None, alias="Abschluss")
    date: Optional[Date] = Field(None, alias="Datum")

    def to_table(self) -> ExamInformationTable:
        return ExamInformationTable(
            ects=self.ects,
            examiner=self.examiner,
            degree_program=self.degree_program,
            kzfa=self.kzfa,
            registration_start=self.registration_start,
            registration_end=self.registration_end,
            exam_id=self.exam_id,
            program_version=self.program_version,
            degree_awarded=self.degree_awarded,
            date=self.date
        )

class AssociatedClass(BaseModel):
    description: Optional[str] = Field(None, alias="Beschreibung")
    weekly_hours: Optional[float] = Field(None)
    number: Optional[str] = Field(None)

    def to_table(self) -> AssociatedClassTable:
        return AssociatedClassTable(
            description=self.description,
            weekly_hours=self.weekly_hours,
            number=self.number
        )


class AssociatedTutorial(BaseModel):
    description: Optional[str] = Field(None, alias="Beschreibung")
    weekly_hours: Optional[float] = Field(None)
    number: Optional[str] = Field(None)

    def to_table(self) -> AssociatedTutorialTable:
        return AssociatedTutorialTable(
            description=self.description,
            weekly_hours=self.weekly_hours,
            number=self.number
        )


class EnrollmentDeadline(BaseModel):
    program_associated_deadline: Optional[str] = Field(None)
    other_deadlines: Optional[str] = Field(None)

    def to_table(self) -> EnrollmentDeadlineTable:
         return EnrollmentDeadlineTable(
             program_associated_deadline=self.program_associated_deadline,
             other_deadlines=self.other_deadlines
         )


class Lecture(BaseModel):
    """Model representing a lecture with various associated data."""

    publish_id: int
    title: str
    tree_paths: Optional[List[TreePath]]
    base_info: Optional[ClassBaseInfo]
    additional_information: Optional[AdditionInformation]
    enrollment_deadline: Optional[EnrollmentDeadline]
    associated_programs: Optional[List[AssociatedProgram]]
    class_materials: Optional[List[ClassMaterial]]
    associated_exams: Optional[List[AssociatedExam]]
    exam_informations: Optional[List[ExamInformation]]
    class_sessions: Optional[List[ClassSession]]
    associated_tutorials: Optional[List[AssociatedTutorial]]
    associated_classes: Optional[List[AssociatedClass]]
    persons: Optional[List[Person]]
    institutions: Optional[List[Institution]]

    @staticmethod
    def publish_id_from_url(url: str) -> int:
        """Extract the publish ID from a lecture URL."""
        match = re.search(r"publishid=(\d+)", url)
        if not match:
            raise ValueError("Invalid URL format, 'publishid' not found")
        return int(match.group(1))

    @classmethod
    def from_tuple(
        cls,
        raw: Tuple[str, str, Optional[List[List[str]]]],
        base_info: Optional[ClassBaseInfo] = None,
        additional_information: Optional[AdditionInformation] = None,
        enrollment_deadline: Optional[EnrollmentDeadline] = None,
        associated_programs: Optional[List[AssociatedProgram]] = None,
        class_materials: Optional[List[ClassMaterial]] = None,
        associated_exams: Optional[List[AssociatedExam]] = None,
        exam_informations: Optional[List[ExamInformation]] = None,
        class_sessions: Optional[List[ClassSession]] = None,
        associated_tutorials: Optional[List[AssociatedTutorial]] = None,
        associated_classes: Optional[List[AssociatedClass]] = None,
        persons: Optional[List[Person]] = None,
        institutions: Optional[List[Institution]] = None,
    ) -> "Lecture":
        """Create a Lecture instance from a tuple containing lecture data."""
        title, url, paths = raw
        tree_paths = [TreePath.from_list(p) for p in paths] if paths else None

        return cls(
            title=title,
            publish_id=cls.publish_id_from_url(url),
            tree_paths=tree_paths,
            base_info=base_info,
            additional_information=additional_information,
            enrollment_deadline=enrollment_deadline,
            associated_programs=associated_programs,
            class_materials=class_materials,
            associated_exams=associated_exams,
            exam_informations=exam_informations,
            class_sessions=class_sessions,
            associated_tutorials=associated_tutorials,
            associated_classes=associated_classes,
            persons=persons,
            institutions=institutions
        )

    def to_dict(self) -> dict:
        """Convert the Lecture instance to a dictionary representation."""
        return {
            "publish_id": self.publish_id,
            "name": self.title,
            "tree_paths": ([path.model_dump(mode="json") for path in self.tree_paths] if self.tree_paths else None),
            "base_info": (self.base_info.model_dump(mode="json") if self.base_info else None),
            "additional_information": (
                self.additional_information.model_dump(mode="json") if self.additional_information else None
            ),
            "enrollment_deadline": (
                self.enrollment_deadline.model_dump(mode="json") if self.enrollment_deadline else None
            ),
            "associated_programs": (
                [prog.model_dump(mode="json") for prog in self.associated_programs]
                if self.associated_programs
                else None
            ),
            "class_materials": (
                [mat.model_dump(mode="json") for mat in self.class_materials] if self.class_materials else None
            ),
            "associated_exams": (
                [exam.model_dump(mode="json") for exam in self.associated_exams] if self.associated_exams else None
            ),
            "exam_informations": (
                [info.model_dump(mode="json") for info in self.exam_informations] if self.exam_informations else None
            ),
            "class_sessions": (
                [session.model_dump(mode="json") for session in self.class_sessions] if self.class_sessions else None
            ),
            "associated_tutorials": (
                [tut.model_dump(mode="json") for tut in self.associated_tutorials]
                if self.associated_tutorials
                else None
            ),
            "associated_classes": (
                [clss.model_dump(mode="json") for clss in self.associated_classes] if self.associated_classes else None
            ),
            "persons": {"connect" : self.get_person_ids()}
        }

    def get_person_ids(self):
        if not self.base_info or not self.persons:
            return []
        return [self.get_person_id(person) for person in self.persons]

    @staticmethod
    def get_person_id(person: Person) -> Optional[str]:
        GET_PERSON_ID_QUERY_NAME = "get_person_id.graphql"
        GRAPHQL_FOLDER_NAME = "graphql"
        directus = DirectusService()
        base_path = Path(__file__).parent.parent
        folder = GRAPHQL_FOLDER_NAME
        query_name = GET_PERSON_ID_QUERY_NAME
        query_path = base_path / folder / query_name

        response = directus.execute_query_file(
            query_path,
            variables={
                "firstName": person.first_name,
                "lastName": person.surname
            },
        )
        persons = response.get("data", {}).get("people", [])
        return persons[0].get("id") if persons else None


    def to_table(self) -> tuple[LectureTable, dict[str, list[BaseModel]]]:
        """Converts the lecture object to a table object and related tables."""
        lecture = LectureTable(
            publish_id=self.publish_id,
            title=self.title
        )

        related: dict[str, list[BaseModel]] = {key: [] for key in [
            "tree_paths", "base_info", "additional_information", "enrollment_deadline",
            "associated_programs", "class_materials", "associated_exams",
            "exam_informations", "class_sessions", "associated_tutorials",
            "associated_classes", "persons", "institutions"
        ]}

        self._one_to_one_to_table("base_info", related, lecture)
        self._one_to_one_to_table("additional_information", related, lecture)
        self._one_to_one_to_table("enrollment_deadline", related, lecture)

        self._one_to_many_to_table("tree_paths", related, lecture)
        self._one_to_many_to_table("associated_programs", related, lecture)
        self._one_to_many_to_table("class_materials", related, lecture)
        self._one_to_many_to_table("associated_exams", related, lecture)
        self._one_to_many_to_table("exam_informations", related, lecture)
        self._one_to_many_to_table("class_sessions", related, lecture)
        self._one_to_many_to_table("associated_tutorials", related, lecture)
        self._one_to_many_to_table("associated_classes", related, lecture)

        self._many_to_many_to_table("persons", related)
        self._many_to_many_to_table("institutions", related)

        return lecture, related


    def _one_to_one_to_table(self, attr: str, related: dict, lecture: LectureTable):
        """Convert a one-to-one relationship to a table object."""
        value = getattr(self, attr, None)
        if value:
            table_obj = value.to_table()
            table_obj.lecture = lecture
            related[attr].append(table_obj)

    def _one_to_many_to_table(self, attr: str, related: dict, lecture: LectureTable):
        """Convert a one-to-many relationship to a list of table objects."""
        values = getattr(self, attr, [])
        for item in values:
            table_obj = item.to_table()
            table_obj.lecture = lecture
            related[attr].append(table_obj)

    def _many_to_many_to_table(self, attr: str, related: dict):
        """Convert a many-to-many relationship to a list of table objects."""
        values = getattr(self, attr, [])
        for item in values:
            related[attr].append(item.to_table())


if __name__ == "__main__":
    person = Person(first_name="Daniel", surname="Altmann", title=None)
    print(Lecture.get_person_id(person))
