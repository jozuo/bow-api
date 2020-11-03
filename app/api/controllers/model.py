from pydantic import BaseModel


class Message(BaseModel):
    detail: str


class EmptyResponse(BaseModel):
    pass
