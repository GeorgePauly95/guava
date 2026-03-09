from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from pydantic import ValidationError
from models import Workouts
from services import get_metrics, store_location
from schemas import Message, WorkoutResponse, WorkoutStartRequest, WorkoutStopRequest
import asyncio
import json

app = FastAPI()


@app.post("/api/workouts")
async def start_workout(workoutStartRequest: WorkoutStartRequest) -> WorkoutResponse:
    created_at = workoutStartRequest.created_at
    workout_id = Workouts.create_workout(created_at)
    return WorkoutResponse(id=workout_id)


@app.patch("/api/workouts/{workout_id}/status")
async def stop_workout(workout_id: int, workoutStopRequest: WorkoutStopRequest):
    stopped_at = workoutStopRequest.stopped_at
    Workouts.stop_workout(workout_id, stopped_at)
    return


@app.websocket("/ws")
async def dispatch_message(websocket: WebSocket):
    await websocket.accept()
    workout_id = None

    async def receive_locations():
        nonlocal workout_id
        try:
            while True:
                try:
                    message = json.loads(await websocket.receive_text())
                    try:
                        Message(**message)
                        if message["type"] == "location":
                            workout_id = message["payload"]["workout_id"]
                            store_location(message["payload"])
                    except ValidationError as e:
                        print("Validation Error: ", e)
                except Exception as e:
                    print("Exception: ", e)
                    # check if this is okay to do. it was done to prevent repeated exceptions
                    break
        except WebSocketDisconnect:
            print("Client disconnected")

    async def update_metrics():
        while True:
            await asyncio.sleep(5)
            if workout_id is not None:
                metrics = await get_metrics(workout_id)
                await websocket.send_text(json.dumps(metrics))

    task = asyncio.create_task(update_metrics())
    await receive_locations()
    task.cancel()
