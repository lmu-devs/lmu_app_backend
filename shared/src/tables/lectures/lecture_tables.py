from sqlalchemy import (
    func, DateTime, ARRAY,
    Column,
    Date,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Time,
    Text
)
from sqlalchemy.orm import relationship
from sqlalchemy import Table

from shared.src.core.database import Base
from shared.src.enums import WeekdayEnum
from shared.src.enums.classes_enum import LectureStartTypeEnum


lecture_persons_table = Table(
    'lecture_persons', Base.metadata,
    Column('lecture_publish_id', Integer, ForeignKey('lectures.publish_id', ondelete='CASCADE')),
    Column('person_id', Integer, ForeignKey('persons.id', ondelete='CASCADE'))
)

lecture_institutions_table = Table(
    'lecture_institutions', Base.metadata,
    Column('lecture_publish_id', Integer, ForeignKey('lectures.publish_id', ondelete='CASCADE')),
    Column('institution_id', Integer, ForeignKey('institutions.id', ondelete='CASCADE'))
)

class TreePathTable(Base):
    __tablename__ = 'tree_paths'

    id = Column(Integer, primary_key=True)
    path = Column(ARRAY(String(255)), nullable=True)
    lecture_publish_id = Column(Integer, ForeignKey('lectures.publish_id'))

    lecture = relationship("LectureTable", back_populates="tree_paths")

class PersonTable(Base):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(100), nullable=False)
    surname = Column(String(100), nullable=False)
    title = Column(String(100), nullable=True)

    lectures = relationship("LectureTable", secondary=lecture_persons_table, back_populates="persons")

class InstitutionTable(Base):
    __tablename__ = 'institutions'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    lectures = relationship("LectureTable", secondary=lecture_institutions_table, back_populates="institutions")


class AssociatedProgramTable(Base):
    __tablename__ = 'associated_programs'

    id = Column(Integer, primary_key=True)
    program_name = Column(String(255), nullable=True)
    module_classification = Column(String(255), nullable=True)
    ects = Column(Integer, nullable=True)
    degree = Column(String(255), nullable=True)
    lecture_publish_id = Column(Integer, ForeignKey('lectures.publish_id'))

    lecture = relationship("LectureTable", back_populates="associated_programs")

class ClassBaseInfoTable(Base):
    __tablename__ = 'class_base_info'

    id = Column(Integer, primary_key=True)
    class_type = Column(String(500), nullable=True)
    class_id = Column(String(500), nullable=True)
    class_cycle = Column(String(500), nullable=True)
    semester = Column(String(500), nullable=True)
    sws = Column(Float, nullable=True)
    max_participants = Column(Integer, nullable=True)
    in_person_type = Column(String(500), nullable=True)
    language = Column(String(500), nullable=True)
    for_exchange_students = Column(Text, nullable=True)
    links = Column(Text, nullable=True)
    sigel = Column(Text, nullable=True)
    lecture_publish_id = Column(Integer, ForeignKey('lectures.publish_id'))

    lecture = relationship("LectureTable", back_populates="base_info", uselist=False)

class ClassSessionTable(Base):
    __tablename__ = 'class_sessions'

    id = Column(Integer, primary_key=True)
    caption = Column(String(255), nullable=True)
    weekday = Column(Enum(WeekdayEnum), nullable=True)
    starting_time = Column(Time, nullable=True)
    ending_time = Column(Time, nullable=True)
    timing_type = Column(Enum(LectureStartTypeEnum), nullable=True)
    rythm = Column(String(255), nullable=True)
    duration_start = Column(Date, nullable=True)
    duration_end = Column(Date, nullable=True)
    room = Column(String(500), nullable=True)
    lecturer = Column(String(500), nullable=True)
    remark = Column(Text, nullable=True)
    cancelled_dates = Column(Text, nullable=True)
    lecture_publish_id = Column(Integer, ForeignKey('lectures.publish_id'))

    lecture = relationship("LectureTable", back_populates="class_sessions")

class ClassMaterialTable(Base):
    __tablename__ = 'class_materials'

    id = Column(Integer, primary_key=True)
    valid_from = Column(Date, nullable=True)
    valid_to = Column(Date, nullable=True)
    file_name = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    lecture_publish_id = Column(Integer, ForeignKey('lectures.publish_id'))

    lecture = relationship("LectureTable", back_populates="class_materials")

class AssociatedExamTable(Base):
    __tablename__ = 'associated_exams'

    id = Column(Integer, primary_key=True)
    module_name = Column(String(255), nullable=True)
    program_name = Column(String(255), nullable=True)
    ects = Column(Integer, nullable=True)
    module_classification = Column(String(255), nullable=True)
    degree = Column(String(100), nullable=True)
    module_id = Column(String(100), nullable=True)
    exam_id = Column(String(100), nullable=True)
    po_version = Column(String(100), nullable=True)
    lecture_publish_id = Column(Integer, ForeignKey('lectures.publish_id'))

    lecture = relationship("LectureTable", back_populates="associated_exams")

class AdditionInformationTable(Base):
    __tablename__ = 'addition_information'

    id = Column(Integer, primary_key=True)
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
    lecture_publish_id = Column(Integer, ForeignKey('lectures.publish_id'))

    lecture = relationship("LectureTable", back_populates="additional_information", uselist=False)

class ExamInformationTable(Base):
    __tablename__ = 'exam_information'

    id = Column(Integer, primary_key=True)
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
    lecture_publish_id = Column(Integer, ForeignKey('lectures.publish_id'))

    lecture = relationship("LectureTable", back_populates="exam_informations")

class AssociatedClassTable(Base):
    __tablename__ = 'associated_classes'

    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=True)
    weekly_hours = Column(Float, nullable=True)
    number = Column(String(100), nullable=True)
    lecture_publish_id = Column(Integer, ForeignKey('lectures.publish_id'))

    lecture = relationship("LectureTable", back_populates="associated_classes")

class AssociatedTutorialTable(Base):
    __tablename__ = 'associated_tutorials'

    id = Column(Integer, primary_key=True)
    description = Column(Text, nullable=True)
    weekly_hours = Column(Float, nullable=True)
    number = Column(String(100), nullable=True)
    lecture_publish_id = Column(Integer, ForeignKey('lectures.publish_id'))

    lecture = relationship("LectureTable", back_populates="associated_tutorials")

class EnrollmentDeadlineTable(Base):
    __tablename__ = 'enrollment_deadlines'

    id = Column(Integer, primary_key=True)
    program_associated_deadline = Column(Text, nullable=True)
    other_deadlines = Column(Text, nullable=True)
    lecture_publish_id = Column(Integer, ForeignKey('lectures.publish_id'))

    lecture = relationship("LectureTable", back_populates="enrollment_deadline", uselist=False)

class LectureTable(Base):
    __tablename__ = 'lectures'

    publish_id = Column(Integer, primary_key=True)
    title = Column(String(500), nullable=False)
    last_updated = Column(DateTime, default=func.now(), onupdate=func.now())

    base_info = relationship("ClassBaseInfoTable", back_populates="lecture", uselist=False, cascade="all, delete")
    additional_information = relationship("AdditionInformationTable", back_populates="lecture", uselist=False, cascade="all, delete")
    enrollment_deadline = relationship("EnrollmentDeadlineTable", back_populates="lecture", uselist=False, cascade="all, delete")

    tree_paths = relationship("TreePathTable", back_populates="lecture", cascade="all, delete")
    associated_programs = relationship("AssociatedProgramTable", back_populates="lecture", cascade="all, delete")
    class_materials = relationship("ClassMaterialTable", back_populates="lecture", cascade="all, delete")
    associated_exams = relationship("AssociatedExamTable", back_populates="lecture", cascade="all, delete")
    exam_informations = relationship("ExamInformationTable", back_populates="lecture", cascade="all, delete")
    class_sessions = relationship("ClassSessionTable", back_populates="lecture", cascade="all, delete")
    associated_tutorials = relationship("AssociatedTutorialTable", back_populates="lecture", cascade="all, delete")
    associated_classes = relationship("AssociatedClassTable", back_populates="lecture", cascade="all, delete")
    persons = relationship("PersonTable", secondary=lecture_persons_table, back_populates="lectures")
    institutions = relationship("InstitutionTable", secondary=lecture_institutions_table, back_populates="lectures")
