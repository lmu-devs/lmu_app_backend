from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from shared.src.core.database import Base


class StreetTable(Base):
    __tablename__ = "streets"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    # Relationships
    buildings = relationship("BuildingTable", back_populates="street")
