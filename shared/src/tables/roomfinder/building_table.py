from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.tables.location_table import LocationTable


class BuildingTable(Base):
    __tablename__ = "buildings"

    id = Column(String, primary_key=True)
    street_id = Column(String, ForeignKey("streets.id"), nullable=False)
    display_name = Column(String, nullable=False)

    # Relationships
    street = relationship("StreetTable", back_populates="buildings")
    building_parts = relationship("BuildingPartTable", back_populates="building")
    location = relationship("BuildingLocationTable", back_populates="building", uselist=False) 



class BuildingLocationTable(Base, LocationTable):
    __tablename__ = "building_locations"

    building_id = Column(String, ForeignKey("buildings.id"), primary_key=True)
    
    # Relationship
    building = relationship("BuildingTable", back_populates="location")