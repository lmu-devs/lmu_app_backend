from data_fetcher.src.core.base_collector import BaseCollector
from data_fetcher.src.university.services.university_service import UniversityService


class UniversityCollector(BaseCollector):
    async def _collect_data(self, db):
        service = UniversityService(db)
        service.add_universities() 