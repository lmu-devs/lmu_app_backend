from typing import List

from sqlalchemy.orm import Session

from data_fetcher.src.sport.crawler.zhs_crawler import ZhsCrawler
from data_fetcher.src.sport.models.sport_models import SportCourse
from shared.src.core.logging import get_sport_fetcher_logger
from shared.src.enums import LanguageEnum
from shared.src.tables.sport.sport_table import (
    SportCourseLocationTable,
    SportCourseTable,
    SportCourseTimeSlotTable,
    SportCourseTranslationTable,
    SportTypeTable,
    SportTypeTranslationTable,
)

logger = get_sport_fetcher_logger(__name__)


class SportService:
    def __init__(self, db: Session):
        self.db = db
        self.logger = get_sport_fetcher_logger(__name__)

    def update_sport_courses(self) -> None:
        """Fetch sport courses from ZHS and add them to the database"""
        try:
            crawler = ZhsCrawler()
            sport_courses = crawler.get_courses()

            # Clear existing data
            self._clear_existing_data()

            # Add new data
            self._add_sport_courses(sport_courses)

            self.db.commit()
            self.logger.info("Successfully updated sport courses in database")

        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to update sport courses: {str(e)}")
            raise

    def _clear_existing_data(self) -> None:
        try:
            # Delete child tables first
            self.db.query(SportCourseTimeSlotTable).delete()
            self.db.query(SportCourseTranslationTable).delete()
            self.db.query(SportCourseTable).delete()
            self.db.query(SportCourseLocationTable).delete()
            # Then delete parent tables
            self.db.query(SportTypeTranslationTable).delete()
            self.db.query(SportTypeTable).delete()

            self.db.commit()
            self.logger.info("Successfully cleared existing sport data")
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error clearing existing data: {str(e)}")
            raise

    def _add_sport_courses(self, sport_courses: List[SportCourse]) -> None:
        """Add sport courses to database"""
        # Keep track of processed course IDs to avoid duplicates
        processed_course_ids = set()

        for sport in sport_courses:
            # Create sport type entry using title as ID
            sport_type = SportTypeTable(id=sport.title)
            self.db.add(sport_type)

            self.db.commit()

            # Add sport type translation
            sport_type_translation = SportTypeTranslationTable(
                sport_type_id=sport.title,
                language=LanguageEnum.GERMAN,
                title=sport.title,
            )
            self.db.add(sport_type_translation)

            # Add individual courses
            for course in sport.courses:
                # Skip if we've already processed this course ID
                if course.id in processed_course_ids:
                    self.logger.warning(f"Skipping duplicate course ID: {course.id}")
                    continue

                processed_course_ids.add(course.id)

                try:
                    # Create course entry
                    course_entry = SportCourseTable(
                        id=course.id,
                        sport_type_id=sport.title,  # Using title as sport_type_id
                        start_date=course.duration.start_date,
                        end_date=course.duration.end_date,
                        instructor=course.instructor,
                        category_id=course.category_id,
                        status_code=course.status_code,
                        is_available=course.is_available,
                        student_price=course.price.student,
                        employee_price=course.price.employee,
                        external_price=course.price.external,
                    )
                    self.db.add(course_entry)

                    # Add course translation
                    course_translation = SportCourseTranslationTable(
                        sport_course_id=course.id,
                        language=LanguageEnum.GERMAN,
                        title=course.name,
                    )
                    self.db.add(course_translation)

                    # Add location if it exists
                    if course.location:
                        location = SportCourseLocationTable(
                            sport_course_id=course.id,
                            address=course.location.address,
                            latitude=course.location.latitude,
                            longitude=course.location.longitude,
                        )
                    self.db.add(location)

                    # Add time slots
                    for slot in course.time_slots:
                        time_slot = SportCourseTimeSlotTable(
                            sport_course_id=course.id,
                            day=slot.day,
                            start_time=slot.start_time,
                            end_time=slot.end_time,
                        )
                        self.db.add(time_slot)

                except Exception as e:
                    self.logger.error(f"Error processing course {course.id}: {str(e)}")
                    continue
