from sqlalchemy import ARRAY, Column, ForeignKey, String
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.tables.location_table import LocationTable


class BuildingTable(Base):
    __tablename__ = "buildings"

    building_part_id = Column(String, primary_key=True)
    building_id = Column(String)
    street_id = Column(String, ForeignKey("streets.id"), nullable=False)
    title = Column(String, nullable=False)
    aliases = Column(ARRAY(String), default=[])

    # Relationships
    street = relationship("StreetTable", back_populates="buildings")
    floors = relationship("FloorTable", back_populates="building")
    location = relationship("BuildingLocationTable", back_populates="building", uselist=False)


class BuildingLocationTable(LocationTable):
    __tablename__ = "building_locations"

    building_id = Column(String, ForeignKey("buildings.building_part_id"), primary_key=True)

    # Relationship
    building = relationship("BuildingTable", back_populates="location")
