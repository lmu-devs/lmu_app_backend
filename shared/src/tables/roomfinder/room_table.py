from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from shared.src.core.database import Base


class RoomTable(Base):
    __tablename__ = "rooms"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    floor_id = Column(String, ForeignKey("floors.id"), nullable=False)
    pos_x = Column(Integer, nullable=False)
    pos_y = Column(Integer, nullable=False)

    # Relationship
    floor = relationship("FloorTable", back_populates="rooms")
