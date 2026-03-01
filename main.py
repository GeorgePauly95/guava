from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from models import Workout, Location
from services import calculate_metrics
import json
import asyncio

app = FastAPI()


# post not get, webhook.
@app.get("/api/workouts")
async def start_workout():
    workout_id = Workout.get_workout_id()
    return workout_id


@app.patch("/api/workouts/{workout_id}/status")
async def stop_workout(workout_id: int):
    Workout.stop_workout(workout_id)
    return


# {"type": "metrics",
# "payload": {
# "latitude":2,
# "longitude": 3,
# "time": 4,
# "workout_id":5
# }
# }


# {"type": "metrics", "payload": {"workout_id":2}}


# validate the message using pydantic classes
# create a update metrics services function
@app.websocket("/ws")
async def dispatch_message(websocket: WebSocket):
    await websocket.accept()
    message = await websocket.receive_text()
    message = json.loads(message)
    if message["type"] == "location":
        Location.store_location(message["payload"])
    elif message["type"] == "metrics":
        workout_id = message["payload"]["workout_id"]
        try:
            while True:
                await asyncio.sleep(5)
                locations = Location.get_workout_locations(workout_id)
                metrics = calculate_metrics(locations)
                await websocket.send_text(json.dumps(metrics))
        except WebSocketDisconnect:
            print("WS disconnected")
