from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from shared.src.tables import CanteenLocationTable, CinemaLocationTable
from shared.src.schemas.location_scheme import Location

class PlacesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_places(self):
        return Location(address="test", latitude=1, longitude=1)
    
    def _get_places_query(self):
        query = select(
            CanteenLocationTable,
            CinemaLocationTable,
        )
        
        return query