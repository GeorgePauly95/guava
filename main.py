from fastapi import FastAPI, WebSocket, Request, Depends
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from models import Workouts, Users
from services import (
    handle_message,
    update_metrics,
    route_modify_workout,
    security,
    handle_google_oauth,
    google_oauth_url,
)
from schemas import (
    Username,
    Message,
    WorkoutStartResponse,
    WorkoutStartRequest,
    WorkoutModifyRequest,
    WorkoutModifyResponse,
)
from services.oauth import encrypt_state, get_redirect_url
from utils import status_code_map
from typing import Annotated
import json
import asyncio

app = FastAPI()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    message = ""
    try:
        request_body = await request.json()
    except Exception as e:
        print(f"{e}")
        request_body = "No body"
    for error in exc.errors():
        message += f"\nField: {error['loc']}\nError: {error['msg']}\nRequest body sent: {request_body}"
    return PlainTextResponse(message, status_code=400)


@app.get("/api/login")
async def login_user(redirect_url: str):
    state = encrypt_state(redirect_url)
    google_oauth_url_with_state = google_oauth_url + f"&state={state}"
    return RedirectResponse(google_oauth_url_with_state, status_code=302)


@app.get("/auth/google/callback")
async def google_auth(code: str, state: str):
    redirect_url = get_redirect_url(state)
    jwt = handle_google_oauth(code)
    headers = {"Authorization": jwt}
    return RedirectResponse(f"http://{redirect_url}", headers=headers)


@app.post("/api/users")
async def create_user(username: Username):
    username = username.username
    user_id = Users.create_user(username)
    return user_id


@app.post("/api/workouts")
async def start_workout(
    user_id: Annotated[int, Depends(security)],
    workoutStartRequest: WorkoutStartRequest,
) -> WorkoutStartResponse:
    started_at = workoutStartRequest.started_at
    workout_id = Workouts.create_workout(user_id, started_at)
    return WorkoutStartResponse(id=workout_id)


@app.patch(
    "/api/workouts/{workout_id}/status",
    responses={
        200: {"model": WorkoutModifyResponse},
        400: {"model": WorkoutModifyResponse},
        404: {"model": WorkoutModifyResponse},
        409: {"model": WorkoutModifyResponse},
    },
)
async def modify_workout(
    user_id: Annotated[int, Depends(security)],
    workout_id: int,
    workoutModifyRequest: WorkoutModifyRequest,
):
    status, time = workoutModifyRequest.status, workoutModifyRequest.modified_at
    response_body = route_modify_workout(user_id, workout_id, status, time)
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

    # TODO: create this task in the global scope.
    # update metrics can be called for all clients instead of being
    # called for each client separately.
    task = asyncio.create_task(update_metrics(websocket))
    await receive_locations()
    task.cancel()
