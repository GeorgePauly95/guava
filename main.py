from fastapi import FastAPI, WebSocket
from models import Workouts
from services import handle_message, update_metrics, handle_status
from schemas import Message, WorkoutResponse, WorkoutStartRequest, WorkoutModifyRequest
import json
import asyncio

app = FastAPI()


@app.post("/api/workouts")
async def start_workout(workoutStartRequest: WorkoutStartRequest) -> WorkoutResponse:
    started_at = workoutStartRequest.started_at
    workout_id = Workouts.create_workout(started_at)
    return WorkoutResponse(id=workout_id)


@app.patch("/api/workouts/{workout_id}/status")
async def stop_workout(workout_id: int, workoutModifyRequest: WorkoutModifyRequest):
    status, time = workoutModifyRequest.status, workoutModifyRequest.modified_at
    handle_status(workout_id, status, time)
    return


@app.websocket("/ws")
async def handle_ws_connection(websocket: WebSocket):
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
