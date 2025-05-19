from fastapi import APIRouter
from app.database import db_dependency
from app.router.auth import user_dependecy

router = APIRouter(
	prefix="/user",
	tags=["user"]
)

@router.get("/current")
async def get_current_user(user: user_dependecy):
	return user