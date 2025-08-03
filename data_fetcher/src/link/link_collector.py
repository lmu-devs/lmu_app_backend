from data_fetcher.src.core.base_collector import BaseCollector
from data_fetcher.src.link.services.link_benefit_service import LinkBenefitService
from data_fetcher.src.link.services.link_resource_service import LinkResourceService


class LinkCollector(BaseCollector):
    async def _collect_data(self, db):
        service = LinkResourceService(db)
        service.run()

        service = LinkBenefitService(db)
        service.run()
