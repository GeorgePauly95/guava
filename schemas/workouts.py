from pydantic import BaseModel
from enum import Enum
from typing import Optional
from datetime import datetime


class WorkoutModifyResponse(BaseModel):
    success: bool
    error: Optional[str] = None
    status: str


class WorkoutStartResponse(BaseModel):
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
