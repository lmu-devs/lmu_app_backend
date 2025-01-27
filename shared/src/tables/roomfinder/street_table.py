from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from shared.src.core.database import Base


class StreetTable(Base):
    __tablename__ = "streets"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    city_id = Column(String, ForeignKey("cities.id"), nullable=False)

    # Relationships
    buildings = relationship("BuildingTable", back_populates="street")
    city = relationship("CityTable", back_populates="streets") 