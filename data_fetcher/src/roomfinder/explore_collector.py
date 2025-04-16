from data_fetcher.src.core.base_collector import BaseCollector
from data_fetcher.src.roomfinder.services.explore_service import RoomfinderService
from shared.src.core.logging import get_roomfinder_fetcher_logger


class RoomfinderCollector(BaseCollector):
    def __init__(self):
        super().__init__()
        self.logger = get_roomfinder_fetcher_logger(__name__)

    async def _collect_data(self, db):
        service = RoomfinderService(db)
        service.update_database()
