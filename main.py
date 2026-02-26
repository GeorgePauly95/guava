from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from models import Workout, Location
from services import calculate_metrics
from engine import engine
import json

app = FastAPI()


# no data input, output is the workout id
@app.get("/api/workouts")
async def start_workout():
    workout_id = Workout.get_workout_id()
    return workout_id


@app.post("/workouts/:id/stop")
async def stop_workout():
    return "workout_id"


# the client should send JSON string:
# '{
#   "lattitude": lattitude,
#   "longitude": longitude,
#   "timestamp": timestamp,
#   "workout_id": workout_id
#   }'
@app.websocket("/api/location")
async def send_location(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        print("location data type:", type(data))
        dict_data = json.loads(data)
        print("location data type:", type(dict_data))
        Location.store_location(dict_data)
        await websocket.send_text(data)


# sends JSON string:
# '{
#   "distance": distance,
#   "time": time,
#   "speed": speed
#   "workout_id": workout_id
# }'
@app.websocket("/api/metrics/:workout_id")
async def send_metrics(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_text("Lorem Ipsum")
    except WebSocketDisconnect:
        print("WS disconnected")
