from pydantic import BaseModel
from datetime import datetime
from enum import Enum


# add status attribute to indicate event, start, stop, resume, pause
# class Workout(BaseModel, Enum):
#     stopped_at: datetime
#     started_at: datetime
#     resumed_at: datetime
#     paused_at: datetime


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
