from pydantic import BaseModel, Field

from api.src.v1.home.models.home_featured_model import FeaturedTiles
from api.src.v1.home.models.home_tile_model import HomeTiles

# class Link(BaseModel):
#     title: str
#     url: str
    
# class TimePeriod(BaseModel):
#     start_date: datetime
#     end_date: datetime
    
# class SemesterFee(BaseModel):
#     fee: float
#     time_period: TimePeriod
#     iban: str
#     bic: str
#     reference: str
#     receiver: str

class Home(BaseModel):
    featured: FeaturedTiles = Field()
    tiles: HomeTiles = Field()