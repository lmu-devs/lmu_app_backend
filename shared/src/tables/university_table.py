from sqlalchemy import Column, Enum, ForeignKey, String
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.enums import UniversityEnum
from shared.src.tables.language_table import LanguageTable


class UniversityTable(Base):
    __tablename__ = "universities"

    id = Column(Enum(UniversityEnum), primary_key=True, nullable=False, index=True)

    translations = relationship(
        "UniversityTranslationTable",
        back_populates="university",
        cascade="all, delete-orphan",
    )
    screenings = relationship("MovieScreeningTable", back_populates="university", cascade="all, delete-orphan")


class UniversityTranslationTable(LanguageTable):
    __tablename__ = "university_translations"

    university_id = Column(
        Enum(UniversityEnum),
        ForeignKey("universities.id", ondelete="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    title = Column(String, nullable=False)

    university = relationship("UniversityTable", back_populates="translations")
