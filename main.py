from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles
from models import Workout, Location

app = FastAPI()


@app.websocket("/api/ws")
async def get_metrics(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Location was {data}")


@app.get("/workout")
async def get_workout_id():
    return "workout_id"
