from pydantic import BaseModel
from datetime import datetime


class Location(BaseModel):
    latitude: float
    longitude: float
    time: str
    workout_id: int


class Message(BaseModel):
    type: str
    payload: Location


class WorkoutId(BaseModel):
    id: int


class Workout(BaseModel):
    created_at: datetime
