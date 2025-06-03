from fastapi import APIRouter, status, HTTPException
from app.database import db_dependency
from app.router.auth import user_dependency
from app.router.user import UserOut
from app.router.genre import GenreOut
from app.router.instrument import InstrumentOut, Instrument
from app.models import User, Genre
from app.util.location import haversine
from typing import List, Optional
from pydantic import BaseModel, conlist, conint

router = APIRouter(
	prefix="/filter",
	tags=["filter"]
)

class Filter(BaseModel):
	instruments: list[int]

class UserFilterOut(UserOut):
	genres: list[GenreOut]
	instruments: list[InstrumentOut]
	distance_km: float

def sort_by_location(current_user: User, users: List[User]):
	users_with_distance = []

	for user in users:
		if user.setup_complete == False or user.latitude is None or user.longitude is None or user is current_user:
			continue
		distance = haversine(current_user.latitude, current_user.longitude, user.latitude, user.longitude)
		user.distance_km = round(distance, 2)
		users_with_distance.append(user)
	
	users_with_distance.sort(key=lambda user: user.distance_km)

	return users_with_distance

@router.get("/location", status_code=status.HTTP_200_OK, response_model=List[UserFilterOut])
async def filter_by_user_location(user: user_dependency, db: db_dependency):
	if user.latitude is None or user.longitude is None:
		raise HTTPException(status_code=400, detail='User has no location specified')

	users = (
		db.query(User)
		.filter(User.id != user.id)
		.all()
	)

	return sort_by_location(user, users)

@router.get("/genre", status_code=status.HTTP_200_OK, response_model=List[UserFilterOut])
async def filter_by_user_genre(user: user_dependency, db: db_dependency):
	user_genre_ids = [genre.id for genre in user.genres]

	users = (
		db.query(User)
		.join(User.genres)
		.filter(Genre.id.in_(user_genre_ids))
		.filter(User.id != user.id)
		.all()
	)

	return sort_by_location(user, users)

@router.post("/instrument", status_code=status.HTTP_200_OK, response_model=List[UserFilterOut])
async def filter_instruments(user: user_dependency, db: db_dependency, filter: Filter):
	users = (
		db.query(User)
		.join(User.genres)
		.join(User.instruments)
		.filter(Instrument.id.in_(filter.instruments))
		.all()
	)

	return sort_by_location(user, users)