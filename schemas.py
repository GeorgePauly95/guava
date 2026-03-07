from pydantic import BaseModel


class Location(BaseModel):
    latitude: float
    longitude: float
    time: str
    workout_id: int


class Message(BaseModel):
    type: str
    payload: Location


class Workout(BaseModel):
    id: int
