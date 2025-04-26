from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    String,
    Time,
    func,
)
from sqlalchemy.orm import relationship

from shared.src.core.database import Base
from shared.src.enums import CanteenTypeEnum, OpeningHoursTypeEnum, WeekdayEnum
from shared.src.tables.image_table import ImageTable
from shared.src.tables.location_table import LocationTable


class CanteenTable(Base):
    __tablename__ = "canteens"

    id = Column(String, primary_key=True, nullable=False)
    name = Column(String, nullable=False)
    type = Column(Enum(CanteenTypeEnum, name="canteen_type"))

    location = relationship(
        "CanteenLocationTable",
        uselist=False,
        back_populates="canteen",
        cascade="all, delete-orphan",
    )
    opening_hours = relationship(
        "CanteenOpeningHoursTable",
        back_populates="canteen",
        cascade="all, delete-orphan",
    )
    images = relationship("CanteenImageTable", back_populates="canteen", cascade="all, delete-orphan")
    status = relationship("CanteenStatusTable", back_populates="canteen", uselist=False)
    likes = relationship("CanteenLikeTable", back_populates="canteen")
    menu_days = relationship("MenuDayTable", back_populates="canteen", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Canteen(id='{self.id}', name='{self.name}')>"

    @property
    def like_count(self):
        return len(self.likes)


class CanteenStatusTable(Base):
    __tablename__ = "canteen_status"

    canteen_id = Column(
        String,
        ForeignKey("canteens.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    )
    is_closed = Column(Boolean, nullable=False)
    is_temporary_closed = Column(Boolean, nullable=False)
    is_lecture_free = Column(Boolean, nullable=False)

    canteen = relationship("CanteenTable", back_populates="status")

    def __repr__(self):
        return f"<CanteenStatus(canteen_id='{self.canteen_id}', is_closed='{self.is_closed}', is_temporary_closed='{self.is_temporary_closed}', is_lecture_free='{self.is_lecture_free}')>"


class CanteenLocationTable(LocationTable):
    __tablename__ = "canteen_locations"

    canteen_id = Column(String, ForeignKey("canteens.id", ondelete="CASCADE"), primary_key=True)

    canteen = relationship("CanteenTable", back_populates="location")


class CanteenOpeningHoursTable(Base):
    __tablename__ = "canteen_opening_hours"

    canteen_id = Column(String, ForeignKey("canteens.id", ondelete="CASCADE"), primary_key=True)
    day = Column(Enum(WeekdayEnum, name="weekday"), primary_key=True)
    type = Column(Enum(OpeningHoursTypeEnum, name="opening_hours_type"), primary_key=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    canteen = relationship("CanteenTable", back_populates="opening_hours")


# Table to represent the many-to-many relationship between dishes and users
class CanteenLikeTable(Base):
    __tablename__ = "canteen_likes"

    canteen_id = Column(String, ForeignKey("canteens.id", ondelete="CASCADE"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    canteen = relationship("CanteenTable", back_populates="likes")
    user = relationship("UserTable", back_populates="liked_canteens")

    def __repr__(self):
        return f"<CanteenLike(canteen_id='{self.canteen_id}', user_id='{self.user_id}')>"


# Table to represent the many-to-many relationship between canteens and images
class CanteenImageTable(ImageTable, Base):
    __tablename__ = "canteen_images"

    canteen_id = Column(String, ForeignKey("canteens.id", ondelete="CASCADE"), nullable=False)

    canteen = relationship("CanteenTable", back_populates="images")

    def __repr__(self):
        return f"<CanteenImage(canteen_id='{self.canteen_id}', name='{self.name}', url='{self.url}', blurhash='{self.blurhash}')>"
