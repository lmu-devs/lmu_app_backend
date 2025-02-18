from data_fetcher.src.core.base_collector import BaseCollector
from data_fetcher.src.links.services.link_service import LinkService


class LinkCollector(BaseCollector):
    async def _collect_data(self, db):
        service = LinkService(db)
        service.merge_links_in_db()