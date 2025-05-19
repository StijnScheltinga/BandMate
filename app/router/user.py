from fastapi import APIRouter, status
from app.models import User
from app.dependencies import db_dependency
from pydantic import BaseModel, Field

router = APIRouter(
	prefix='/user',
	tags=['user']
)

class CreateUserRequest(BaseModel):
	email: str = Field(max_length=255)
	password: str = Field(max_length=255)
	display_name: str = Field(max_length=255)
	latitude: float | None
	longtitude: float | None

	class Config:
		json_schema_extra = {
			"example": {
				"email": "user@gmail.com",
				"password": "password123!",
				"display_name": "John doe",
				"latitude": 52.1326,
				"longtitude": 5.2913
			}
		}

@router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
	new_user = User(
		email=create_user_request.email,
		hashed_password=create_user_request.password,
		display_name=create_user_request.display_name,
		latitude=create_user_request.latitude,
		longtitude=create_user_request.longtitude
	)
	db.add(new_user)
	db.commit()

