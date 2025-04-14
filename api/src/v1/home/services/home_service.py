from sqlalchemy.orm import Session

from api.src.v1.home.models.home_model import Home
from api.src.v1.home.models.home_tile_model import (BaseHomeTile, HomeTileEnum,
                                                    HomeTiles)
from shared.src.core.logging import get_food_logger
from shared.src.enums.language_enums import LanguageEnum

logger = get_food_logger(__name__)


class HomeService:
    def __init__(self, db: Session, language: LanguageEnum):
        self.db = db
        self.language = language

    # def get_semester_fee(self):
    #     return SemesterFee(
    #         fee=85.00,
    #         receiver="LMU München",
    #         iban="DE54 7005 0000 3701 1903 15",
    #         bic="BYLADEMM",
    #         reference="Matrikelnr/20251/LMU Rueckmeldung SoSe 2025",
    #         time_period=TimePeriod(
    #             start_date=datetime(2024, 12, 4),
    #             end_date=datetime(2025, 2, 8)
    #             )
    #         )

    async def get_tiles(self):
        # screenings_service = ScreeningService(self.db, self.language)
        # screenings = await screenings_service.get_movie_screenings()
        # up to 4 screenings today and after
        # screenings = [screening for screening in screenings if screening.date >= datetime.now()]
        # screenings = screenings[:4]

        # logger.info(f"Screenings: {screenings}")
        # screenings = MovieScreenings.from_table(screenings)
        return HomeTiles(
            root=[
                BaseHomeTile(
                    type=HomeTileEnum.TIMELINE,
                    size=1,
                    title="Timeline",
                ),
                BaseHomeTile(
                    type=HomeTileEnum.ROOMFINDER,
                    size=1,
                    title="Roomfinder",
                ),
                BaseHomeTile(
                    type=HomeTileEnum.SPORTS,
                    size=1,
                    title="Sports",
                    description="124 courses",
                ),
                BaseHomeTile(
                    type=HomeTileEnum.CINEMAS,
                    size=1,
                    title="Cinema",
                ),
                BaseHomeTile(
                    type=HomeTileEnum.LINKS,
                    size=1,
                    title="Links",
                    description="12 links",
                ),
                BaseHomeTile(
                    type=HomeTileEnum.BENEFITS,
                    size=1,
                    title="Benefits",
                    description="4 offers",
                ),
                BaseHomeTile(
                    type=HomeTileEnum.WISHLIST,
                    size=1,
                    title="Wishlist",
                    description="7 features",
                ),
                BaseHomeTile(
                    type=HomeTileEnum.FEEDBACK,
                    size=1,
                    title="Feedback",
                    description="für die App",
                ),
                # BaseHomeTile(
                #     type=HomeTileEnum.NEWS,
                #     size=1,
                #     title="News",
                #     description="+ 3 this week"
                # ),
                # BaseHomeTile(
                #     type=HomeTileEnum.EVENTS,
                #     size=1,
                #     title="Events",
                #     description="Events"
                # ),
            ]
        )

    async def get_home_data(self):
        # TODO: make dynamic
        return Home(featured=[], tiles=await self.get_tiles())
