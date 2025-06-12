from fastapi import APIRouter, status, HTTPException
from app.database import db_dependency
from app.router.auth import user_dependency, pw_context
from app.models import User
from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import List, Optional
from app.responses import unauthorized
import re

router = APIRouter(
	prefix="/user",
	tags=["user"]
)

class CreateUserRequest(BaseModel):
	email: EmailStr = Field(max_length=255)
	password: str = Field(max_length=255)

	@field_validator("password")
	@classmethod
	def validate_password(cls, value: str):
		if len(value) < 8:
			raise ValueError("Password must be at least 8 characters long")
		if not re.search(r"[A-Z]", value):
			raise ValueError("Password must contain at least one uppercase letter")
		if not re.search(r"[a-z]", value):
			raise ValueError("Password must contain at least one lowercase letter")
		if not re.search(r"\d", value):
			raise ValueError("Password must contain at least one digit")
		if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
			raise ValueError("Password must contain at least one special character")
		return value

	class Config:
		json_schema_extra = {
			"example": {
				"email": "user@gmail.com",
				"password": "Password123!",
			}
		}

class UserOut(BaseModel):
	id: int
	email: str
	display_name: Optional[str] = None
	latitude: Optional[float] = None
	longitude: Optional[float] = None
	distance_km: Optional[float] = None
	profile_picture: Optional[str] = None
	city: Optional[str] = None

@router.post('/create_user', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
	if db.query(User).filter(User.email == create_user_request.email).first():
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An user with this email already exists")
	new_user = User(
		email=create_user_request.email,
		hashed_password=pw_context.hash(create_user_request.password),
	)
	db.add(new_user)
	db.commit()

        return {"message": "successfully created user"}

@router.get("/current", status_code=status.HTTP_200_OK, response_model=UserOut, responses=unauthorized)
async def get_current_user(user: user_dependency):
	return user

@router.get("/all", status_code=status.HTTP_200_OK, response_model=List[UserOut], responses=unauthorized)
async def get_all_users(user: user_dependency, db: db_dependency):
	return db.query(User).all()

@router.delete('/delete', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency):
	db.delete(user)
	db.commit()