from typing import List

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, relationship

from shared.src.db.base_class import Base
from shared.src.models.opening_hours.base import BaseOpeningHours, BaseTimeRangeModel


class SportCourseTimeRange(BaseTimeRangeModel):
    __tablename__ = "sport_course_time_ranges"

    opening_hours_id = Column(Integer, ForeignKey("sport_course_opening_hours.id"))
    location = Column(String, nullable=True)  # Specific room or location for the course
    instructor = Column(String, nullable=True)  # Optional instructor information

    opening_hours = relationship("SportCourseOpeningHours", back_populates="time_ranges")


class SportCourseOpeningHours(Base, BaseOpeningHours):
    __tablename__ = "sport_course_opening_hours"

    sport_course_id = Column(Integer, ForeignKey("sport_courses.id"), nullable=False)

    # Relationships
    sport_course = relationship("SportCourse", back_populates="opening_hours")
    time_ranges: Mapped[List[SportCourseTimeRange]] = relationship(
        "SportCourseTimeRange",
        back_populates="opening_hours",
        cascade="all, delete-orphan",
    )

    @property
    def time_range_class(self):
        return SportCourseTimeRange
