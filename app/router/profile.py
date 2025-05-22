from fastapi import APIRouter, status
from app.database import db_dependency
from app.router.auth import user_dependency
from app.models import User, Genre, Instrument
from pydantic import BaseModel, Field
from typing import List, Optional

router = APIRouter(
	prefix='/profile',
	tags=['profile']
)

class ProfileInfo(BaseModel):
	display_name: str
	genre_ids: List[int]
	instrument_ids: List[int]
	latitude: float
	longitude: float

	class Config:
		json_schema_extra = {
			"example": {
				"display_name": "user123",
				"genre_ids": [1, 3, 19],
				"instrument_ids": [4, 7, 13],
				"latitude": 52.719474,
				"longitude": 5.075181
			}
		}

@router.post('/setup', status_code=status.HTTP_201_CREATED)
async def set_profile_info(user: user_dependency, db: db_dependency, profile_info: ProfileInfo):

	genres_to_add = db.query(Genre).filter(Genre.id.in_(profile_info.genre_ids)).all()
	user.genres.extend(genres_to_add)

	instruments_to_add = db.query(Instrument).filter(Instrument.id.in_(profile_info.instrument_ids)).all()
	user.instruments.extend(instruments_to_add)

	user.display_name = profile_info.display_name
	user.latitude = profile_info.latitude
	user.longitude = profile_info.longitude

	db.commit()

