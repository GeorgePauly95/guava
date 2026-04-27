from fastapi import APIRouter
from schemas import Username
from models import Users

user = APIRouter(prefix="/users", tags=["users"])


@user.post("/")
async def create_user(username: Username):
    username = username.username
    user_id = Users.create_user(username)
    return user_id
