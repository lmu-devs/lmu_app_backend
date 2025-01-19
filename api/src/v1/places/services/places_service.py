from sqlalchemy import literal, select, union_all
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.places.schemas.places_scheme import Place, PlaceEnum
from shared.src.tables import CanteenLocationTable, CinemaLocationTable


class PlacesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_places(self):
        # Query canteens and cinemas separately and combine results
        canteen_result = await self.db.execute(
            select(CanteenLocationTable)
        )
        cinema_result = await self.db.execute(
            select(CinemaLocationTable)
        )
        
        # Get all results as ORM objects
        canteens = canteen_result.scalars().all()
        cinemas = cinema_result.scalars().all()
        
        # Combine the results
        return [*canteens, *cinemas]