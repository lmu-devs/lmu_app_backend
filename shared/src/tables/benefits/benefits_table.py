from sqlalchemy import ARRAY, Column, Integer, String

from shared.src.core.database import Base


class BenefitTable(Base):
    __tablename__ = "benefits"
    id = Column(Integer, primary_key=True)
