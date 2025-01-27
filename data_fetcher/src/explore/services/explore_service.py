import json
from typing import List

from sqlalchemy.orm import Session

from data_fetcher.src.explore.models import Building, BuildingPart, City, Floor, Room, Street
from shared.src.tables.explore import (
    BuildingLocationTable,
    BuildingPartTable,
    BuildingTable,
    CityTable,
    FloorTable,
    RoomTable,
    StreetTable,
)


class ExploreService:
    def __init__(self, db: Session):
        self.db = db

    def update_database(self) -> None:
        """Updates all explore related tables in the database"""
        self._update_cities()
        self._update_streets()
        self._update_buildings()
        self._update_building_parts()
        self._update_floors()
        self._update_rooms()
        self.db.commit()

    def _update_cities(self) -> None:
        """Updates cities table with data from 1_city.json"""
        with open('data_fetcher/src/explore/constants/1_city.json') as f:
            city_data = json.load(f)
            cities = City.from_json_list(city_data)
            
        for city in cities:
            self.db.merge(CityTable(
                id=city.code,
                name=city.name
            ))
        self.db.flush()

    def _update_streets(self) -> None:
        """Updates streets table with data from 2_street.json"""
        with open('data_fetcher/src/explore/constants/2_street.json') as f:
            street_data = json.load(f)
            streets = Street.from_json_list(street_data)
            
        for street in streets:
            self.db.merge(StreetTable(
                id=street.code,
                name=street.name,
                city_id=street.cityCode
            ))
        self.db.flush()

    def _update_buildings(self) -> None:
        """Updates buildings and building_locations tables with data from 3_building.json"""
        with open('data_fetcher/src/explore/constants/3_building.json') as f:
            building_data = json.load(f)
            buildings = Building.from_json_list(building_data)
            
        for building in buildings:
            self.db.merge(BuildingTable(
                id=building.code,
                street_id=building.streetCode,
                display_name=building.displayName
            ))
            self.db.merge(BuildingLocationTable(
                building_id=building.code,
                address=building.displayName.capitalize().replace(" - ", ""),
                latitude=building.lat,
                longitude=building.lng
            ))
        self.db.flush()

    def _update_building_parts(self) -> None:
        """Updates building_parts table with data from 4_building_part.json"""
        with open('data_fetcher/src/explore/constants/4_building_part.json') as f:
            building_part_data = json.load(f)
            building_parts = BuildingPart.from_json_list(building_part_data)
            
        for building_part in building_parts:
            self.db.merge(BuildingPartTable(
                id=building_part.code,
                building_id=building_part.buildingCode,
                address=building_part.address
            ))
        self.db.flush()

    def _update_floors(self) -> None:
        """Updates floors table with data from 5_floor.json"""
        with open('data_fetcher/src/explore/constants/5_floor.json') as f:
            floor_data = json.load(f)
            floors = Floor.from_json_list(floor_data)
            
        for floor in floors:
            self.db.merge(FloorTable(
                id=floor.code,
                building_part_id=floor.buildingPart,
                level=floor.level,
                name=floor.name,
                map_uri=floor.mapUri,
                map_size_x=floor.mapSizeX,
                map_size_y=floor.mapSizeY
            ))
        self.db.flush()

    def _update_rooms(self) -> None:
        """Updates rooms table with data from 6_room.json"""
        with open('data_fetcher/src/explore/constants/6_room.json') as f:
            room_data = json.load(f)
            rooms = Room.from_json_list(room_data)
            
        for room in rooms:
            self.db.merge(RoomTable(
                id=room.code,
                name=room.name,
                floor_id=room.floorCode,
                pos_x=room.posX,
                pos_y=room.posY
            ))
        self.db.flush()


if __name__ == "__main__":
    with open('data_fetcher/src/explore/constants/1_city.json') as f:
        city_data = json.load(f)
        cities = City.from_json_list(city_data)
    
        print(cities)
        
    with open('data_fetcher/src/explore/constants/2_street.json') as f:
        street_data = json.load(f)
        streets = Street.from_json_list(street_data)
        print(streets)

    with open('data_fetcher/src/explore/constants/3_building.json') as f:
        building_data = json.load(f)
        buildings = Building.from_json_list(building_data)
        print(buildings)
        
        # print all display names
        for building in buildings:
            print(building.displayName.capitalize().replace(" - ", ""))

