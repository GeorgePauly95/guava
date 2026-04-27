from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from schemas import (
    WorkoutStartResponse,
    WorkoutStartRequest,
    WorkoutModifyRequest,
    WorkoutModifyResponse,
)
from models import Workouts
from typing import Annotated
from services import security, route_modify_workout
from utils import status_code_map

workout = APIRouter(prefix="/workouts", tags=["workouts"])
User_id = Annotated[int, Depends(security)]


@workout.get("/")
async def get_workouts(user_id: User_id):
    Workouts.get_workouts(user_id)
    pass


@workout.post("/")
async def start_workout(
    user_id: User_id,
    workoutStartRequest: WorkoutStartRequest,
) -> WorkoutStartResponse:
    started_at = workoutStartRequest.started_at
    workout_id = Workouts.create_workout(user_id, started_at)
    return WorkoutStartResponse(id=workout_id)


@workout.patch(
    "/{workout_id}/status",
    responses={
        200: {"model": WorkoutModifyResponse},
        400: {"model": WorkoutModifyResponse},
        404: {"model": WorkoutModifyResponse},
        409: {"model": WorkoutModifyResponse},
    },
)
async def modify_workout(
    user_id: User_id,
    workout_id: int,
    workoutModifyRequest: WorkoutModifyRequest,
):
    status, time = workoutModifyRequest.status, workoutModifyRequest.modified_at
    response_body = route_modify_workout(user_id, workout_id, status, time)
    return JSONResponse(
        status_code=status_code_map(response_body["status"]), content=response_body
    )
