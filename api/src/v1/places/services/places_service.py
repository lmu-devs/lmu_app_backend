from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.tables import (
    BuildingLocationTable,
    CanteenLocationTable,
    CinemaLocationTable,
)


class PlacesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_places(self):
        # Query canteens and cinemas separately and combine results
        canteen_result = await self.db.execute(select(CanteenLocationTable))
        cinema_result = await self.db.execute(select(CinemaLocationTable))
        building_result = await self.db.execute(select(BuildingLocationTable))

        # Get all results as ORM objects
        canteens = canteen_result.scalars().all()
        cinemas = cinema_result.scalars().all()
        buildings = building_result.scalars().all()
        # Combine the results
        return [*canteens, *cinemas, *buildings]
