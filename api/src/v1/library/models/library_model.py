from typing import List
from uuid import UUID

from pydantic import BaseModel, RootModel

from shared.src.enums import WeekdayEnum
from shared.src.models.image_model import Images
from shared.src.models.location_model import Location
from shared.src.models.rating_model import Rating
from shared.src.tables.library.library_table import (
    LibraryTable,
    LibraryTranslationTable,
)


class TimeRange(BaseModel):
    start: str
    end: str


class OpeningDay(BaseModel):
    day: str
    timeframes: List[TimeRange]


class OpeningHours(BaseModel):
    days: List[OpeningDay]


class PhoneContact(BaseModel):
    number: str
    recipient: str | None = None

    @classmethod
    def from_table(cls, phone_data: List[dict]):
        """Convert phone data from translation to PhoneContact objects."""
        return [cls(**phone) for phone in phone_data] if phone_data else []


class Service(BaseModel):
    title: str
    description: str | None = None

    @classmethod
    def from_table(cls, services_data: List[dict]):
        """Convert services data from translation to Service objects."""
        return [cls(**service) for service in services_data] if services_data else []


class Equipment(BaseModel):
    title: str
    url: str | None = None
    type: str | None = None
    description: str | None = None

    @classmethod
    def from_table(cls, equipment_data: List[dict]):
        """Convert equipment data from translation to Equipment objects."""
        return [cls(**equip) for equip in equipment_data] if equipment_data else []


class Library(BaseModel):
    id: str
    name: str
    hash: str
    url: str
    external_url: str | None = None
    reservation_url: str | None = None
    rating: Rating
    images: Images | None = Images(root=[])
    location: Location | None = None
    phones: List[PhoneContact] = []
    opening_hours: OpeningHours | None = None
    services: List[Service] = []
    equipment: List[Equipment] = []
    subject_areas: List[str] = []
    liked: bool = False

    @classmethod
    def from_table(cls, library: LibraryTable, user_id: UUID = None):
        # Get the first translation (should be the best match due to ordering in the query)
        translation: LibraryTranslationTable = library.translations[0] if library.translations else None

        # Extract basic information
        name = translation.name if translation else "Not translated"
        services = []
        equipment = []
        subject_areas = []

        # Extract translation data
        if translation:
            if translation.services:
                services = Service.from_table(translation.services)
            if translation.equipment:
                equipment = Equipment.from_table(translation.equipment)
            if translation.subject_areas:
                subject_areas = translation.subject_areas

        # Create images model
        images = Images.from_table(library.images)
        location = Location.from_table(library.location)

        # Create contact model
        phone = []
        if library.phone:
            phone = PhoneContact.from_table(library.phone)

        # Create opening hours model
        opening_hours = None
        if library.opening_hours:
            days = []
            for weekday in WeekdayEnum:
                day_hours = [oh for oh in library.opening_hours if oh.weekday == weekday]
                if day_hours:
                    timeframes = []
                    for oh in day_hours:
                        if oh.time_ranges:
                            for time_range in oh.time_ranges:
                                if time_range.get("start_time") and time_range.get("end_time"):
                                    timeframes.append(
                                        TimeRange(
                                            start=time_range.get("start_time"),
                                            end=time_range.get("end_time"),
                                        )
                                    )
                    if timeframes:  # Only add days that have actual timeframes
                        days.append(OpeningDay(day=weekday.value, timeframes=timeframes))
            if days:  # Only create OpeningHours if we have days with timeframes
                opening_hours = OpeningHours(days=days)

        # Determine if user has liked this library
        user_likes_library = None
        if user_id:
            user_likes_library = any(like.user_id == user_id for like in library.likes)

        # Create rating model
        rating = Rating.from_params(like_count=library.like_count, is_liked=user_likes_library)

        return cls(
            id=library.id,
            name=name,
            hash=library.hash,
            url=library.url,
            external_url=library.external_url,
            reservation_url=library.reservation_url,
            rating=rating,
            images=images,
            location=location,
            phone=phone,
            opening_hours=opening_hours,
            services=services,
            equipment=equipment,
            subject_areas=subject_areas,
            liked=user_likes_library if user_likes_library is not None else False,
        )


class Libraries(RootModel):
    root: List[Library]

    @classmethod
    def from_table(cls, libraries, user_id: UUID = None):
        """Convert a list of library tables to a Libraries pydantic model.

        Args:
            libraries: List of LibraryTable objects
            user_id: Optional user ID to check like status

        Returns:
            Libraries model containing all converted Library objects
        """
        return cls([Library.from_table(library, user_id) for library in libraries])
