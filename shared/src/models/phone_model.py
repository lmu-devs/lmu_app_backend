from pydantic import BaseModel, Field, RootModel


class Phone(BaseModel):
    number: str = Field(..., description="The phone number")
    recipient: str | None = Field(None, description="The recipient of the phone number, if it is known")


class Phones(RootModel):
    root: list[Phone]
