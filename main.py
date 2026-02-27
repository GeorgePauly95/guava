from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from models import Workout, Location
from services import calculate_metrics
import json
import asyncio

app = FastAPI()


@app.get("/api/workouts")
async def start_workout():
    workout_id = Workout.get_workout_id()
    return workout_id


@app.post("/api/workouts/{workout_id}/stop")
async def stop_workout(workout_id: int):
    Workout.stop_workout(workout_id)
    return


@app.websocket("/api/location")
async def receive_location(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        dict_data = json.loads(data)
        Location.store_location(dict_data)


@app.websocket("/api/metrics/{workout_id}")
async def send_metrics(websocket: WebSocket, workout_id: int):
    await websocket.accept()
    try:
        while True:
            await asyncio.sleep(5)
            locations = Location.get_workout_locations(workout_id)
            metrics = calculate_metrics(locations)
            await websocket.send_text(json.dumps(metrics))
    except WebSocketDisconnect:
        print("WS disconnected")
