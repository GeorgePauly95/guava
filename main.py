from fastapi import (
    FastAPI,
    Request,
    WebSocket,
    WebSocketException,
    WebSocketDisconnect,
    status,
)
from fastapi.responses import PlainTextResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from routers import users, workouts
from services import (
    update_metrics,
    handle_google_oauth,
    google_oauth_url,
    encrypt_state,
    get_redirect_url,
)
from schemas import Message, Data
from services.authentication import verify_jwt
from utils import connection_manager
from db import FitnessData
from services.queue import dispatch_message
from contextlib import asynccontextmanager
import json
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(update_metrics(connection_manager))
    yield
    task.cancel()


app = FastAPI(lifespan=lifespan)
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


@app.post("/api/data", summary="ingest all data")
async def create_data(data: Data):
    """
    Any fitness data in JSON format can be sent.
    The top level fields should be:
    - **user**
    - **data**

    The user field should be an object.
    The object should could contain the following mandatory field:
    - **email**

    Any other user info can also be sent in other fields
    with the following types:
    - **str**
    - **int**
    - **float**
    """
    data = data.model_dump_json()
    return PlainTextResponse(FitnessData.ingest_data(data), status_code=201)


@app.get("/api/v1/login")
async def login_user(redirect_url: str):
    state = encrypt_state(redirect_url)
    google_oauth_url_with_state = google_oauth_url + f"&state={state}"
    return RedirectResponse(google_oauth_url_with_state, status_code=302)


@app.get("/api/v0/auth/google/callback")
async def google_auth_v0(code: str, state: str):
    redirect_url = get_redirect_url(state)
    jwt = handle_google_oauth(code)
    response = RedirectResponse(f"{redirect_url}?token={jwt}")
    return response


@app.get("/api/v1/auth/google/callback")
async def google_auth(code: str, state: str):
    redirect_url = get_redirect_url(state)
    jwt = handle_google_oauth(code)
    headers = {"Authorization": f"Bearer {jwt}"}
    response = RedirectResponse(f"{redirect_url}", headers=headers)
    return response


# TODO: Use HTTP header and not query parameter to get JWT.
@app.websocket("/ws")
async def handle_ws_messages(websocket: WebSocket, token: str):
    user_id = verify_jwt(token)
    if not user_id:
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)

    await connection_manager.create_connection(user_id, websocket)
    try:
        while True:
            try:
                message = json.loads(await websocket.receive_text())
                print("MESSAGE:\n", message)
                Message(**message)
                dispatch_message(message)
            except WebSocketDisconnect:
                print(f"Client: {user_id} disconnected")
                break
            except Exception as e:
                print("Error Message:\n", e)
    finally:
        connection_manager.remove_connection(user_id)
