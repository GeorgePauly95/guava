from pydantic import BaseModel, Field
from datetime import datetime


class EventData(BaseModel):
    type: str
    data: int | float | str


class LogEventData(BaseModel):
    time: int = Field(..., ge=0, le=int(datetime.now().timestamp()))
    event: EventData


class User(BaseModel):
    email: str


class Data(BaseModel):
    data: LogEventData
    user: User
