from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from shared.src.core.database import Base


class CityTable(Base):
    __tablename__ = "cities"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    # Relationships
    streets = relationship("StreetTable", back_populates="city") 