from datetime import datetime
from uuid import uuid4

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Time,
    func,
)
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.enums import WeekdayEnum
from shared.src.tables import LanguageTable
from shared.src.tables.location_table import LocationTable


class SportTypeTable(Base):
    __tablename__ = "sport_type"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    translations = relationship("SportTypeTranslationTable", back_populates="sport_type")
    sport_courses = relationship("SportCourseTable", back_populates="sport_type")


class SportTypeTranslationTable(LanguageTable):
    __tablename__ = "sport_type_translation"

    sport_type_id = Column(String, ForeignKey("sport_type.id"), primary_key=True)
    title = Column(String, nullable=False)

    # Relationship
    sport_type = relationship("SportTypeTable", back_populates="translations")


class SportCourseTable(Base):
    __tablename__ = "sport_course"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Data from ZHS
    sport_type_id = Column(String, ForeignKey("sport_type.id"), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    instructor = Column(String)
    category_id = Column(Integer)
    status_code = Column(Integer)
    is_available = Column(Boolean, default=False)

    # Prices
    student_price = Column(Float)
    employee_price = Column(Float)
    external_price = Column(Float)

    # Relationships
    sport_type = relationship("SportTypeTable", back_populates="sport_courses")
    translations = relationship("SportCourseTranslationTable", back_populates="sport_course")
    time_slots = relationship("SportCourseTimeSlotTable", back_populates="sport_course")
    location = relationship("SportCourseLocationTable", uselist=False, back_populates="sport_course")


class SportCourseTranslationTable(LanguageTable):
    __tablename__ = "sport_course_translation"

    sport_course_id = Column(String, ForeignKey("sport_course.id"), primary_key=True, nullable=False)
    title = Column(String, nullable=False)

    # Relationship
    sport_course = relationship("SportCourseTable", back_populates="translations")


class SportCourseTimeSlotTable(Base):
    __tablename__ = "sport_course_time_slot"

    id = Column(UUID, primary_key=True, default=uuid4)
    sport_course_id = Column(String, ForeignKey("sport_course.id"), nullable=False)
    day = Column(Enum(WeekdayEnum), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    # Relationship
    sport_course = relationship("SportCourseTable", back_populates="time_slots")


class SportCourseLocationTable(LocationTable):
    __tablename__ = "sport_course_location"

    sport_course_id = Column(String, ForeignKey("sport_course.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    sport_course = relationship("SportCourseTable", back_populates="location")
