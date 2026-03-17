from fastapi import FastAPI, WebSocket
from fastapi.responses import JSONResponse
from models import Workouts
from services import handle_message, update_metrics, route_modify_workout
from schemas import (
    Message,
    WorkoutStartResponse,
    WorkoutStartRequest,
    WorkoutModifyRequest,
    WorkoutModifyResponse,
)
from utils import status_code_map
import json
import asyncio

app = FastAPI()


@app.post("/api/workouts")
async def start_workout(
    workoutStartRequest: WorkoutStartRequest,
) -> WorkoutStartResponse:
    started_at = workoutStartRequest.started_at
    workout_id = Workouts.create_workout(started_at)
    return WorkoutStartResponse(id=workout_id)


@app.patch(
    "/api/workouts/{workout_id}/status",
    responses={
        200: {"model": WorkoutModifyResponse},
        404: {"model": WorkoutModifyResponse},
        409: {"model": WorkoutModifyResponse},
        400: {"model": WorkoutModifyResponse},
    },
)
async def modify_workout(workout_id: int, workoutModifyRequest: WorkoutModifyRequest):
    status, time = workoutModifyRequest.status, workoutModifyRequest.modified_at
    response_body = route_modify_workout(workout_id, status, time)
    return JSONResponse(
        status_code=status_code_map(response_body["status"]), content=response_body
    )


@app.websocket("/ws")
async def handle_ws_messages(websocket: WebSocket):
    await websocket.accept()

    async def receive_locations():
        while True:
            try:
                message = json.loads(await websocket.receive_text())
                Message(**message)
                handle_message(message)
            except Exception as e:
                print(e)
                break

    task = asyncio.create_task(update_metrics(websocket))
    await receive_locations()
    task.cancel()
