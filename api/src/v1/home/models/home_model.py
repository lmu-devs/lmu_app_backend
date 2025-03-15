from pydantic import BaseModel

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
    featured: list[str] = []
    tiles: HomeTiles