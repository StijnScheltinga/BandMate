from fastapi import APIRouter, status
from app.database import db_dependency
from app.router.auth import user_dependency
from app.models import User, Genre
from pydantic import BaseModel
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
	distance_km: Optional[float] = None

class UserGenreUpdate(BaseModel):
	genre_ids: List[int]

@router.get("/current", status_code=status.HTTP_200_OK, response_model=UserOut)
async def get_current_user(user: user_dependency):
	return user

@router.get("/all", status_code=status.HTTP_200_OK, response_model=List[UserOut])
async def get_all_users(user: user_dependency, db: db_dependency):
	return db.query(User).all()

# First check wether the given genres are already present in the user, if new genres are present add to user 
@router.post("/add_genre", status_code=status.HTTP_201_CREATED)
async def add_genre(user: user_dependency, db: db_dependency, user_genre_update: UserGenreUpdate):
	existing_genre_ids = {genre.id for genre in user.genres}
	print(f"exisiting genre id's: {existing_genre_ids}")

	genres_to_add = (
		db.query(Genre)
		.filter(Genre.id.in_(user_genre_update.genre_ids))
		.filter(~Genre.id.in_(existing_genre_ids))
		.all()
	)

	if not genres_to_add:
		return {"message": "No new genres to add."}

	user.genres.extend(genres_to_add)
	db.commit()

	return {
        "message": f"Added {len(genres_to_add)} new genres to user.",
        "genre_ids_added": [genre.id for genre in genres_to_add],
    }