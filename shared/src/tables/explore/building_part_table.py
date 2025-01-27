from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from shared.src.core.database import Base


class BuildingPartTable(Base):
    __tablename__ = "building_parts"

    id = Column(String, primary_key=True)
    building_id = Column(String, ForeignKey("buildings.id"), nullable=False)
    address = Column(String, nullable=False)

    # Relationships
    floors = relationship("FloorTable", back_populates="building_part_rel")
    building = relationship("BuildingTable", back_populates="building_parts")