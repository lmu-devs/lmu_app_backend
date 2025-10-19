from sqlalchemy import (
    func,
    DateTime,
    ARRAY,
    Column,
    Date,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Time,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy import Table

from shared.src.core.database import Base
from shared.src.enums import WeekdayEnum
from shared.src.enums.courses_enums import CourseStartTypeEnum

CASCADE_OPTION = "all, delete-orphan"


class BaseTable:
    id = Column(Integer, primary_key=True)


course_persons_association = Table(
    "course_person_association",
    Base.metadata,
    Column(
        "course_publish_id",
        Integer,
        ForeignKey("courses.publish_id", ondelete="CASCADE"),
    ),
    Column("person_id", Integer, ForeignKey("course_persons.id", ondelete="CASCADE")),
)

course_institutions_association = Table(
    "course_institutions_association",
    Base.metadata,
    Column(
        "course_publish_id",
        Integer,
        ForeignKey("courses.publish_id", ondelete="CASCADE"),
    ),
    Column(
        "institution_id",
        Integer,
        ForeignKey("course_institutions.id", ondelete="CASCADE"),
    ),
)


class CourseTreePathTable(Base, BaseTable):
    __tablename__ = "course_tree_paths"

    path = Column(ARRAY(String(255)), nullable=True)
    course_publish_id = Column(Integer, ForeignKey("courses.publish_id"))

    course = relationship("CourseTable", back_populates="tree_paths")


class CoursePersonTable(Base, BaseTable):
    __tablename__ = "course_persons"

    first_name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    title = Column(String(100), nullable=True)

    courses = relationship(
        "CourseTable",
        secondary=course_persons_association,
        back_populates="persons",
    )


class CourseInstitutionTable(Base, BaseTable):
    __tablename__ = "course_institutions"

    name = Column(String(255), nullable=False)

    courses = relationship(
        "CourseTable",
        secondary=course_institutions_association,
        back_populates="institutions",
    )


class CourseAssociatedProgramTable(Base, BaseTable):
    __tablename__ = "course_associated_programs"

    program_name = Column(String(255), nullable=True)
    module_classification = Column(String(255), nullable=True)
    ects = Column(Integer, nullable=True)
    degree = Column(String(255), nullable=True)
    course_publish_id = Column(Integer, ForeignKey("courses.publish_id"))

    course = relationship("CourseTable", back_populates="associated_programs")


class CourseBaseInfoTable(Base, BaseTable):
    __tablename__ = "course_base_info"

    type = Column(String(500), nullable=True)
    course_id = Column(String(500), nullable=True)
    cycle = Column(String(500), nullable=True)
    semester = Column(String(500), nullable=True)
    sws = Column(Float, nullable=True)
    max_participants = Column(Integer, nullable=True)
    in_person_type = Column(String(500), nullable=True)
    language = Column(String(500), nullable=True)
    for_exchange_students = Column(Text, nullable=True)
    links = Column(Text, nullable=True)
    sigel = Column(Text, nullable=True)
    course_publish_id = Column(Integer, ForeignKey("courses.publish_id"))

    course = relationship("CourseTable", back_populates="base_info", uselist=False)


class CourseSessionTable(Base, BaseTable):
    __tablename__ = "course_sessions"

    caption = Column(String(255), nullable=True)
    weekday = Column(Enum(WeekdayEnum, native_enum=False), nullable=True)
    starting_time = Column(Time, nullable=True)
    ending_time = Column(Time, nullable=True)
    timing_type = Column(Enum(CourseStartTypeEnum, native_enum=False), nullable=True)
    rythm = Column(String(255), nullable=True)
    duration_start = Column(Date, nullable=True)
    duration_end = Column(Date, nullable=True)
    room = Column(String(500), nullable=True)
    lecturer = Column(String(500), nullable=True)
    remark = Column(Text, nullable=True)
    cancelled_dates = Column(Text, nullable=True)
    course_publish_id = Column(Integer, ForeignKey("courses.publish_id"))

    course = relationship("CourseTable", back_populates="sessions")


class CourseMaterialTable(Base, BaseTable):
    __tablename__ = "course_materials"

    valid_from = Column(Date, nullable=True)
    valid_to = Column(Date, nullable=True)
    file_name = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    course_publish_id = Column(Integer, ForeignKey("courses.publish_id"))

    course = relationship("CourseTable", back_populates="materials")


class CourseAssociatedExamTable(Base, BaseTable):
    __tablename__ = "course_associated_exams"

    module_name = Column(String(255), nullable=True)
    program_name = Column(String(255), nullable=True)
    ects = Column(Integer, nullable=True)
    module_classification = Column(String(255), nullable=True)
    degree = Column(String(100), nullable=True)
    module_id = Column(String(100), nullable=True)
    exam_id = Column(String(100), nullable=True)
    po_version = Column(String(100), nullable=True)
    course_publish_id = Column(Integer, ForeignKey("courses.publish_id"))

    course = relationship("CourseTable", back_populates="associated_exams")


class CourseAdditionInformationTable(Base, BaseTable):
    __tablename__ = "course_additional_information"

    remark = Column(Text, nullable=True)
    literature = Column(Text, nullable=True)
    date = Column(Text, nullable=True)
    registration = Column(Text, nullable=True)
    format = Column(Text, nullable=True)
    content = Column(Text, nullable=True)
    learning_content = Column(Text, nullable=True)
    target_group = Column(Text, nullable=True)
    location = Column(Text, nullable=True)
    comment = Column(Text, nullable=True)
    assessment = Column(Text, nullable=True)
    time = Column(Text, nullable=True)
    topic = Column(Text, nullable=True)
    short_comment = Column(Text, nullable=True)
    prerequisites = Column(Text, nullable=True)
    number = Column(Text, nullable=True)
    type = Column(Text, nullable=True)
    course_publish_id = Column(Integer, ForeignKey("courses.publish_id"))

    course = relationship(
        "CourseTable", back_populates="additional_information", uselist=False
    )


class CourseExamInformationTable(Base, BaseTable):
    __tablename__ = "course_exam_information"

    ects = Column(Integer, nullable=True)
    examiner = Column(String(255), nullable=True)
    degree_program = Column(String(255), nullable=True)
    kzfa = Column(String(255), nullable=True)
    registration_start = Column(Date, nullable=True)
    registration_end = Column(Date, nullable=True)
    exam_id = Column(String(100), nullable=True)
    program_version = Column(String(100), nullable=True)
    degree_awarded = Column(String(255), nullable=True)
    date = Column(Date, nullable=True)
    course_publish_id = Column(Integer, ForeignKey("courses.publish_id"))

    course = relationship("CourseTable", back_populates="exam_information")


class CourseAssociatedClassTable(Base, BaseTable):
    __tablename__ = "course_associated_classes"

    description = Column(Text, nullable=True)
    weekly_hours = Column(Float, nullable=True)
    number = Column(String(100), nullable=True)
    course_publish_id = Column(Integer, ForeignKey("courses.publish_id"))

    course = relationship("CourseTable", back_populates="associated_classes")


class CourseAssociatedTutorialTable(Base, BaseTable):
    __tablename__ = "course_associated_tutorials"

    description = Column(Text, nullable=True)
    weekly_hours = Column(Float, nullable=True)
    number = Column(String(100), nullable=True)
    course_publish_id = Column(Integer, ForeignKey("courses.publish_id"))

    course = relationship("CourseTable", back_populates="associated_tutorials")


class CourseEnrollmentDeadlineTable(Base, BaseTable):
    __tablename__ = "course_enrollment_deadlines"

    program_associated_deadline = Column(Text, nullable=True)
    other_deadlines = Column(Text, nullable=True)
    course_publish_id = Column(Integer, ForeignKey("courses.publish_id"))

    course = relationship(
        "CourseTable", back_populates="enrollment_deadline", uselist=False
    )


class CourseTable(Base):
    __tablename__ = "courses"

    publish_id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())

    base_info = relationship(
        "CourseBaseInfoTable",
        back_populates="course",
        uselist=False,
        cascade=CASCADE_OPTION,
    )
    additional_information = relationship(
        "CourseAdditionInformationTable",
        back_populates="course",
        uselist=False,
        cascade=CASCADE_OPTION,
    )
    enrollment_deadline = relationship(
        "CourseEnrollmentDeadlineTable",
        back_populates="course",
        uselist=False,
        cascade=CASCADE_OPTION,
    )

    tree_paths = relationship(
        "CourseTreePathTable", back_populates="course", cascade=CASCADE_OPTION
    )
    associated_programs = relationship(
        "CourseAssociatedProgramTable",
        back_populates="course",
        cascade=CASCADE_OPTION,
    )
    materials = relationship(
        "CourseMaterialTable",
        back_populates="course",
        cascade=CASCADE_OPTION,
    )
    associated_exams = relationship(
        "CourseAssociatedExamTable",
        back_populates="course",
        cascade=CASCADE_OPTION,
    )
    exam_information = relationship(
        "CourseExamInformationTable",
        back_populates="course",
        cascade=CASCADE_OPTION,
    )
    sessions = relationship(
        "CourseSessionTable", back_populates="course", cascade=CASCADE_OPTION
    )
    associated_tutorials = relationship(
        "CourseAssociatedTutorialTable",
        back_populates="course",
        cascade=CASCADE_OPTION,
    )
    associated_classes = relationship(
        "CourseAssociatedClassTable",
        back_populates="course",
        cascade=CASCADE_OPTION,
    )
    persons = relationship(
        "CoursePersonTable",
        secondary=course_persons_association,
        back_populates="courses",
    )
    institutions = relationship(
        "CourseInstitutionTable",
        secondary=course_institutions_association,
        back_populates="courses",
    )
