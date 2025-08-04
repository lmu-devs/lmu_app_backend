from typing import List
from uuid import UUID

from pydantic import BaseModel, RootModel

from api.src.v1.core.sql_image_transform_utils import transform_library_files_to_images
from shared.src.models.image_model import Images
from shared.src.models.location_model import Location
from shared.src.models.rating_model import Rating
from shared.src.tables.library.library_area_table import (
    LibraryAreaOpeningHoursTable,
    LibraryAreaTable,
)
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

    @classmethod
    def from_table(cls, opening_hours: LibraryAreaOpeningHoursTable):
        if not opening_hours:
            return None

        # Convert from 'start_time'/'end_time' format to 'start'/'end' format
        formatted_timeframes = []
        for time_range in opening_hours.time_ranges:
            formatted_timeframes.append(TimeRange(start=time_range.get("start_time"), end=time_range.get("end_time")))

        return cls(day=opening_hours.weekday, timeframes=formatted_timeframes)


class LibraryArea(BaseModel):
    id: int
    name: str
    opening_hours: List[OpeningDay] | None = None

    @classmethod
    def from_table(cls, area: LibraryAreaTable):
        """Convert a single area table to LibraryArea model"""
        if not area:
            return None
        if not area.translations:
            return None
        for translation in area.translations:
            opening_hours = [OpeningDay.from_table(day) for day in area.opening_hours] if area.opening_hours else None
            return cls(
                id=area.id,
                name=translation.name,
                opening_hours=opening_hours,
            )


class LibraryAreas(RootModel):
    root: List[LibraryArea]

    @classmethod
    def from_table(cls, areas: List[LibraryAreaTable]) -> List["LibraryArea"]:
        """Convert a list of area tables to a list of LibraryArea models"""
        if not areas:
            return []
        result = []
        for area in areas:
            area_model = LibraryArea.from_table(area)
            if area_model:
                result.append(area_model)
        return result


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
        equipment_list = [cls(**equip) for equip in equipment_data] if equipment_data else []
        return cls.sort_by_priority(equipment_list)

    @staticmethod
    def sort_by_priority(equipment_list: List["Equipment"]) -> List["Equipment"]:
        """Sort equipment list with priority:
        1. Items with both links and descriptions
        2. Items with only descriptions
        3. Items with only links
        4. The rest
        """

        def get_priority(item: "Equipment") -> int:
            has_url = item.url is not None and item.url != ""
            has_description = item.description is not None and item.description != ""

            if has_url and has_description:
                return 0  # Highest priority
            elif has_description:
                return 1
            elif has_url:
                return 2
            else:
                return 3  # Lowest priority

        return sorted(equipment_list, key=get_priority)


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
    areas: List[LibraryArea] = []
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
                subject_areas = sorted(translation.subject_areas)

        # Create images model from files using the new utility
        images = Images(root=[])
        if hasattr(library, "files") and library.files:
            images = transform_library_files_to_images(library.files)

        location = None
        if library.location:
            location = Location.from_table(library.location)

        # Create contact model
        phone = []
        if library.phone:
            phone = PhoneContact.from_table(library.phone)

        # Create areas from table - using the new from_areas method for the list
        areas = LibraryAreas.from_table(library.areas)

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
            phones=phone,
            areas=areas,
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
