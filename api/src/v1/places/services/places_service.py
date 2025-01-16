from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.src.v1.places.schemas.places_scheme import Place, PlaceEnum
from shared.src.schemas.location_scheme import Location
from shared.src.tables import CanteenLocationTable, CinemaLocationTable


class PlacesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_places(self):
        query = self._get_places_query()
        result = await self.db.execute(query)
        places = result.scalars().all()
        
        for place in places:
            print(f"place: {place.latitude}, {place.longitude}, {place.address}")
            
        return places
    
    def _get_places_query(self):
        query = select(
            CanteenLocationTable,
            CinemaLocationTable,
        )
        
        return query