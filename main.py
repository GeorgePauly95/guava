from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, ValidationError
from models import Workouts
from services import get_metrics, store_location
import asyncio
import json

app = FastAPI()


class Location_payload(BaseModel):
    latitude: float
    longitude: float
    time: str
    workout_id: int


class Message(BaseModel):
    type: str
    payload: Location_payload


class Workout(BaseModel):
    id: int


@app.post("/api/workouts")
async def start_workout() -> Workout:
    workout_id = Workouts.get_workout_id()
    return Workout(id=workout_id)


@app.patch("/api/workouts/{workout_id}/status")
async def stop_workout(workout_id: int):
    Workouts.stop_workout(workout_id)
    return


# create a update metrics services function
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
