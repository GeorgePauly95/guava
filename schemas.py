from pydantic import BaseModel
from datetime import datetime
from enum import Enum


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


class Status(str, Enum):
    STOP = "stop"
    PAUSE = "pause"
    RESUME = "resume"


class WorkoutModifyRequest(BaseModel):
    status: Status
    modified_at: datetime
