from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.tables.language_table import LanguageTable


class FacultyTable(Base):
    __tablename__ = "faculties"

    id = Column(String, primary_key=True)

    translations = relationship(
        "FacultyTranslationTable",
        back_populates="faculty",
        cascade="all, delete-orphan",
    )


class FacultyTranslationTable(LanguageTable):
    __tablename__ = "faculty_translations"

    faculty_id = Column(
        String,
        ForeignKey("faculties.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    title = Column(String, nullable=False)

    faculty = relationship("FacultyTable", back_populates="translations")
