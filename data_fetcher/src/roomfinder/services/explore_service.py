import json

from sqlalchemy.orm import Session

from data_fetcher.src.roomfinder.models import Building, Floor, Room, Street
from shared.src.tables.roomfinder import (
    BuildingLocationTable,
    BuildingTable,
    FloorTable,
    RoomTable,
    StreetTable,
)


class RoomfinderService:
    def __init__(self, db: Session):
        self.db = db
        self.streets = self._get_streets()
        self.buildings = self._get_buildings()
        self.floors = self._get_floors()
        self.rooms = self._get_rooms()

    def _get_streets(self) -> list[Street]:
        with open("data_fetcher/src/roomfinder/constants/2_street.json") as f:
            street_data = json.load(f)
            return Street.from_json_list(street_data)

    def _get_buildings(self) -> list[Building]:
        with open("data_fetcher/src/roomfinder/constants/3_building.json") as f:
            building_data = json.load(f)
            return Building.from_json_list(building_data)

    def _get_floors(self) -> list[Floor]:
        with open("data_fetcher/src/roomfinder/constants/5_floor.json") as f:
            floor_data = json.load(f)
            return Floor.from_json_list(floor_data)

    def _get_rooms(self) -> list[Room]:
        with open("data_fetcher/src/roomfinder/constants/6_room.json") as f:
            room_data = json.load(f)
            return Room.from_json_list(room_data)

    def update_database(self) -> None:
        """Updates all explore related tables in the database"""
        self._update_streets()
        self._update_buildings()
        self._update_floors()
        self._update_rooms()
        self.db.commit()

    def _update_streets(self) -> None:
        """Updates streets table with data from 2_street.json"""

        for street in self.streets:
            self.db.merge(StreetTable(id=street.code, name=street.name))
        self.db.flush()

    def _update_buildings(self) -> None:
        """Updates buildings and building_locations tables with data from 3_building.json"""

        for building in self.buildings:
            self.db.merge(
                BuildingTable(
                    building_part_id=building.buildingPartCode,
                    building_id=building.buildingCode,
                    street_id=building.streetCode,
                    title=building.title,
                    aliases=building.aliases,
                )
            )
            self.db.merge(
                BuildingLocationTable(
                    building_id=building.buildingPartCode,
                    address=building.address,
                    latitude=building.lat,
                    longitude=building.lng,
                )
            )
        self.db.flush()

    def _update_floors(self) -> None:
        """Updates floors table with data from 5_floor.json"""

        for floor in self.floors:
            self.db.merge(
                FloorTable(
                    id=floor.code,
                    building_part_id=floor.buildingPartCode,
                    level=floor.level,
                    name=floor.name,
                    map_uri=floor.mapUri,
                    map_size_x=floor.mapSizeX,
                    map_size_y=floor.mapSizeY,
                )
            )
        self.db.flush()

    def _update_rooms(self) -> None:
        """Updates rooms table with data from 6_room.json"""

        for room in self.rooms:
            self.db.merge(
                RoomTable(
                    id=room.code,
                    name=room.name,
                    floor_id=room.floorCode,
                    pos_x=room.posX,
                    pos_y=room.posY,
                )
            )
        self.db.flush()


if __name__ == "__main__":

    with open("data_fetcher/src/roomfinder/constants/2_street.json") as f:
        street_data = json.load(f)
        streets = Street.from_json_list(street_data)
        print(streets)

    with open("data_fetcher/src/roomfinder/constants/3_building.json") as f:
        building_data = json.load(f)
        buildings = Building.from_json_list(building_data)
        print(buildings)

        # print all display names
        for building in buildings:
            print(building.title)
