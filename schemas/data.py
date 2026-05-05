from pydantic import BaseModel


class LogEventData(BaseModel):
    time: int
    value: int | float | str


class User(BaseModel):
    email: str


class BaseData(BaseModel):
    data: LogEventData
    user: User
