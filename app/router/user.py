from fastapi import APIRouter, status
from app.database import db_dependency
from app.router.auth import user_dependency
from app.models import User, Genre
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter(
	prefix="/user",
	tags=["user"]
)

class UserOut(BaseModel):
	id: int
	email: str
	display_name: str
	latitude: float
	longitude: float
	distance_km: float = Field(default=None)

@router.get("/current", status_code=status.HTTP_200_OK, response_model=UserOut)
async def get_current_user(user: user_dependency):
	return user

@router.get("/all", status_code=status.HTTP_200_OK, response_model=List[UserOut])
async def get_all_users(user: user_dependency, db: db_dependency):
	return db.query(User).all()

@router.delete('/delete', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency):
	db.delete(user)
	db.commit()