from pydantic import BaseModel, Field, RootModel

class FeaturedTile(BaseModel):
    title: str = Field()
    description: str = Field()
    path: str = Field()
    priority: int = Field()




class FeaturedTiles(RootModel):
    root: list[FeaturedTile]