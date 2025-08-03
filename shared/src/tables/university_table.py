from sqlalchemy import Column, Integer, String

from shared.src.core.database import Base


class UniversityTable(Base):
    __tablename__ = "universities"

    id = Column(Integer, primary_key=True, nullable=False, index=True)
    abbreviation = Column(String, nullable=False)
