from fastapi import FastAPI, WebSocket
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

# @app.websocket("/api/ws")
# async def track_position(websocket: WebSocket):
