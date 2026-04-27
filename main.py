from fastapi import FastAPI, WebSocket, Request, APIRouter
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from routers import users, workouts
from services import (
    handle_message,
    update_metrics,
    handle_google_oauth,
    google_oauth_url,
)
from schemas import (
    Message,
)
from services.oauth import encrypt_state, get_redirect_url
import json
import asyncio

app = FastAPI()
app.include_router(workouts.workout, prefix="/api")
app.include_router(users.user, prefix="/api")


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
    headers = {"Authorization": f"Bearer {jwt}"}
    response = RedirectResponse(f"{redirect_url}", headers=headers)
    return response


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
