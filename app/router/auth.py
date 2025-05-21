from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, Field
from app.models import User
from app.database import db_dependency
from app.config import settings
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from zoneinfo import ZoneInfo
from jose import jwt, JWTError
from typing import Annotated

pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

router = APIRouter(
	prefix='/auth',
	tags=['auth']
)

class CreateUserRequest(BaseModel):
	email: str = Field(max_length=255)
	password: str = Field(max_length=255)
	display_name: str = Field(max_length=255)
	latitude: float | None
	longitude: float | None

	class Config:
		json_schema_extra = {
			"example": {
				"email": "user@gmail.com",
				"password": "password123!",
				"display_name": "John doe",
				"latitude": 52.1326,
				"longitude": 5.2913
			}
		}
	
class Token(BaseModel):
	access_token: str
	token_type: str

def authenticate_user(email, password, db: db_dependency):
	user = db.query(User).filter(User.email == email).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	if not pw_context.verify(password, user.hashed_password):
		raise HTTPException(status_code=401, detail="Incorrect Password")
	return user

def create_acces_token(email: str, user_id: int, expires_delta: timedelta):
	encode = {"sub": email, "user_id": user_id}
	expires = datetime.now(ZoneInfo("UTC")) + expires_delta
	encode.update({"exp": expires})
	return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def hash_password(password: str):
	return pw_context.hash(password)

async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)], db: db_dependency):
	try:
		payload = jwt.decode(token, SECRET_KEY, ALGORITHM)
		email: str = payload.get('sub')
		user_id: int = payload.get('user_id')
		if email is None or user_id is None:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
		current_user = db.query(User).filter(User.id == user_id).first()
		return current_user
	except JWTError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user')
	

@router.post("/token", response_model=Token)
async def get_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
	user = authenticate_user(form_data.username, form_data.password, db)
	token = create_acces_token(user.email, user.id, timedelta(minutes=30))
	return {"access_token": token, "token_type": "bearer"}


@router.post('/create_user', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
	if db.query(User).filter(User.email == create_user_request.email).first():
		raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An user with this email already exists")
	new_user = User(
		email=create_user_request.email,
		hashed_password=pw_context.hash(create_user_request.password),
		display_name=create_user_request.display_name,
		latitude=create_user_request.latitude,
		longitude=create_user_request.longitude
	)
	db.add(new_user)
	db.commit()

user_dependency = Annotated[User, Depends(get_current_user)]