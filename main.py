from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post("/workout")
async def workout(request: Request):
    body = await request.body()
    print(body)
    return body
