from fastapi import FastAPI, WebSocket, Request, Depends, HTTPException
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from models import Workouts, Users
from services import (
    handle_message,
    update_metrics,
    route_modify_workout,
    create_jwt,
    verify_jwt,
)
from schemas import (
    Message,
    WorkoutStartResponse,
    WorkoutStartRequest,
    WorkoutModifyRequest,
    WorkoutModifyResponse,
)
from auth import (
    google_oauth_url,
    google_token_url,
    google_client_id,
    google_client_secret,
    google_redirect_url,
    google_user_info_url,
)
from utils import status_code_map
from dotenv import load_dotenv
from typing import Annotated
import json
import asyncio
import httpx
import os

load_dotenv()

app = FastAPI()

secret_key = os.getenv("SECRET_KEY").encode("utf-8")

http_bearer = HTTPBearer()


def security(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(http_bearer)],
):
    jwt = credentials.credentials
    user_id = verify_jwt(jwt)
    if user_id:
        return user_id
    raise HTTPException(status_code=401)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    message = ""
    for error in exc.errors():
        message += f"\nField: {error['loc']}\nError: {error['msg']}\nRequest body sent: {await request.json()}"
    return PlainTextResponse(message, status_code=400)


@app.get("/")
async def home(user_id: Annotated[int, Depends(security)]):
    return {"user_id": user_id}


@app.get("/api/login")
async def login_user():
    print("OAuth URL:", google_oauth_url)
    return RedirectResponse(google_oauth_url, status_code=302)


@app.get("/auth/google/callback")
async def google_auth(request: Request):
    code = request.query_params.get("code")
    request_body = {
        "code": code,
        "client_id": google_client_id,
        "client_secret": google_client_secret,
        "redirect_uri": google_redirect_url,
        "grant_type": "authorization_code",
    }
    token_response = httpx.post(google_token_url, data=request_body)
    token_response_body = token_response.json()
    access_token = token_response_body.get("access_token")
    user_info_response = httpx.get(
        google_user_info_url, headers={"Authorization": f"Bearer {access_token}"}
    )
    user_info_response_body = user_info_response.json()
    google_id = user_info_response_body["id"]
    username = user_info_response_body["email"]
    user_id = Users.get_or_create_by_google_id(google_id, username)
    jwt = create_jwt(user_id, secret_key)
    return RedirectResponse(f"http://localhost:8000?token={jwt}")


# TODO: given username return user_id
# TODO: use pydantic model instead of using request class
@app.post("/api/users")
async def create_user(request: Request):
    request_body = await request.json()
    username = request_body["username"]
    user_id = Users.create_user(username)
    return user_id


@app.post("/api/users/{user_id}/workouts")
async def start_workout(
    user_id: int,
    workoutStartRequest: WorkoutStartRequest,
) -> WorkoutStartResponse:
    started_at = workoutStartRequest.started_at
    workout_id = Workouts.create_workout(user_id, started_at)
    return WorkoutStartResponse(id=workout_id)


@app.patch(
    "/api/users/{user_id}/workouts/{workout_id}/status",
    responses={
        200: {"model": WorkoutModifyResponse},
        400: {"model": WorkoutModifyResponse},
        404: {"model": WorkoutModifyResponse},
        409: {"model": WorkoutModifyResponse},
    },
)
async def modify_workout(
    user_id: int, workout_id: int, workoutModifyRequest: WorkoutModifyRequest
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
