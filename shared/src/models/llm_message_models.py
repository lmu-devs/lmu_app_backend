from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str = Field(description="The role of the message")
    content: str = Field(description="The content of the message")


class SystemMessage(Message):
    role: str = "system"


class UserMessage(Message):
    role: str = "user"


class AssistantMessage(Message):
    role: str = "assistant"
