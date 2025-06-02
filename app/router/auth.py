from fastapi import APIRouter, status, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from app.models import User
from app.database import db_dependency
from app.config import settings
from datetime import datetime, timedelta
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from zoneinfo import ZoneInfo
from jose import jwt, JWTError, ExpiredSignatureError
from typing import Annotated

pw_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM

router = APIRouter(
	prefix='/auth',
	tags=['auth']
)
	
class Token(BaseModel):
	access_token: str
	refresh_token: str
	token_type: str

class RefreshToken(BaseModel):
	access_token: str
	token_type: str

def authenticate_user(email, password, db: db_dependency):
	user = db.query(User).filter(User.email == email).first()
	if not user:
		raise HTTPException(status_code=404, detail="User not found")
	if not pw_context.verify(password, user.hashed_password):
		raise HTTPException(status_code=401, detail="Incorrect Password")
	return user

def create_token(email: str, user_id: int, expires_delta: timedelta):
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
	access_token = create_token(user.email, user.id, timedelta(minutes=15))
	refresh_token = create_token(user.email, user.id, timedelta(days=7))
	user.refresh_token = refresh_token
	db.add(user)
	db.commit()
	return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}

@router.post("/refresh", status_code=status.HTTP_200_OK, response_model=RefreshToken)
async def refresh_token(db: db_dependency, refresh_token: str = Body(...)):
	try:
		payload = jwt.decode(refresh_token, SECRET_KEY, ALGORITHM)
		user_email = payload.get('sub')
		user = db.query(User).filter(User.email == user_email).first()
		if (refresh_token == user.refresh_token):
			access_token = create_token(user.email, user.id, timedelta(minutes=15))
			return {"access_token": access_token, "token_type": "bearer"}
		else:
			raise HTTPException(status_code=401, detail="Invalid refresh token")
	except ExpiredSignatureError:
		raise HTTPException(status_code=401, detail="Refresh token expired")
	except JWTError:
		raise HTTPException(status_code=401, detail="Invalid refresh token")

user_dependency = Annotated[User, Depends(get_current_user)]