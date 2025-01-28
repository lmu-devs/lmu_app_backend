from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.src.tables.roomfinder import BuildingPartTable, FloorTable, BuildingTable, RoomTable, StreetTable, CityTable

class RoomfinderService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_rooms(self):
        result = await self.db.execute(select(RoomTable))
        return result.scalars().all()
    
    async def get_building_parts(self, id: str):
        result = await self.db.execute(select(BuildingTable).where(BuildingTable.id == id))
        return result.scalars().all()
    
    async def get_all(self):
        result = await self.db.execute(
            select(CityTable)
            .join(StreetTable)
            .join(BuildingTable)
            .join(BuildingPartTable)
            .join(FloorTable)
            .join(RoomTable)
        )
        return result.scalars().all()


