from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship
from shared.database import Base
from shared.tables.language_table import LanguageTable

class UniversityTable(Base):
    __tablename__ = "universities"

    id = Column(String, primary_key=True, nullable=False, index=True)
    
    translations = relationship("UniversityTranslationTable", back_populates="university", cascade="all, delete-orphan")
    screenings = relationship("MovieScreeningTable", back_populates="university", cascade="all, delete-orphan")

class UniversityTranslationTable(LanguageTable, Base):
    __tablename__ = "university_translations"

    university_id = Column(String, ForeignKey("universities.id", ondelete='CASCADE'), nullable=False, primary_key=True)
    title = Column(String, nullable=False)
    
    university = relationship("UniversityTable", back_populates="translations")
