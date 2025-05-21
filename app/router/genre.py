from app.models import User, Genre
from fastapi import APIRouter, status
from app.router.auth import user_dependency
from app.database import db_dependency
from typing import List
from pydantic import BaseModel

router = APIRouter(
	prefix='/genre',
	tags=['genre']
)

class UserGenreUpdate(BaseModel):
	genre_ids: List[int]

@router.get("/user", status_code=status.HTTP_200_OK)
async def get_user_genres(user: user_dependency, db: db_dependency):
	genres = user.genres
	return genres

@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_genres(user: user_dependency, db: db_dependency):
	genres = db.query(Genre).all()
	return genres

@router.post("/user/add", status_code=status.HTTP_201_CREATED)
async def add_genre_to_user(user: user_dependency, db: db_dependency, user_genre_update: UserGenreUpdate):
	existing_genre_ids = {genre.id for genre in user.genres}

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

# @router.delete("/user/remove/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def remove_genre_from_user(user: user_dependency, db: db_dependency, genre_id: int):
# 	existing_genre_ids = {genre.id for genre in user.genres}

# 	if genre_id in existing_genre_ids:
