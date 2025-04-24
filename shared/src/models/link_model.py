from pydantic import BaseModel, Field, RootModel


class Link(BaseModel):
    title: str = Field(..., description="The title of the link")
    url: str = Field(..., description="The URL of the link")
    alt: str | None = Field(None, description="The alternative text of the link")


class Links(RootModel):
    root: list[Link]
