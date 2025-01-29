from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from shared.src.tables.roomfinder import BuildingPartTable, BuildingTable, CityTable, FloorTable, RoomTable, StreetTable


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
            .options(
                selectinload(CityTable.streets)
                .selectinload(StreetTable.buildings)
                .selectinload(BuildingTable.location),
                selectinload(CityTable.streets)
                .selectinload(StreetTable.buildings)
                .selectinload(BuildingTable.building_parts)
                .selectinload(BuildingPartTable.floors)
                .selectinload(FloorTable.rooms)
            )
        )
        return result.scalars().all()


