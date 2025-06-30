from data_fetcher.src.core.base_collector import BaseCollector
from data_fetcher.src.people.services.people_service import PeopleService

class PeopleCollector(BaseCollector):
    async def _collect_data(self, db):
        service = PeopleService(db)
        service.collect_and_store_people()