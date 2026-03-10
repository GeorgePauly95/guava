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


class WorkoutResponse(BaseModel):
    id: int


class WorkoutStartRequest(BaseModel):
    started_at: datetime


class WorkoutStopRequest(BaseModel):
    stopped_at: datetime
