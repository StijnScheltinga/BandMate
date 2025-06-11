from app.models import Genre
from app.scripts.startup import GENRES
from fastapi import APIRouter, status, HTTPException
from app.router.auth import user_dependency
from app.database import db_dependency
from typing import List
from pydantic import BaseModel

router = APIRouter(
	prefix='/genre',
	tags=['genre'],
	responses={401: {"description": "unauthorized"}}
)

class UserGenreUpdate(BaseModel):
	genre_ids: List[int]

class GenreOut(BaseModel):
	id: int
	name: str

@router.get("/all", status_code=status.HTTP_200_OK, response_model=List[GenreOut])
async def get_all_genres(user: user_dependency, db: db_dependency):
	genres = db.query(Genre).all()
	return genres

@router.get("/user", status_code=status.HTTP_200_OK, response_model=List[GenreOut], )
async def get_user_genres(user: user_dependency):
	genres = user.genres
	return genres

@router.put("/user", status_code=status.HTTP_200_OK, responses={404: {"description": "Genre id not found"}})
async def update_genres_user(user: user_dependency, db: db_dependency, user_genre_update: UserGenreUpdate):
	"""
	Logic for updating: 
	Genre in update and in current, do nothing
	Genre in update not in current, add
	Genre not in update in current, remove
	"""
	current_user_genre_ids = {genre.id for genre in user.genres}

	# Get genre IDs from the request payload
	updated_genre_ids = set(user_genre_update.genre_ids)

	genres = db.query(Genre).all()
	genre_ids_in_database = [genre.id for genre in genres]
	
	for g_id in updated_genre_ids:
		if g_id not in genre_ids_in_database:
			raise HTTPException(status_code=404, detail=f"Id {g_id} does not exist")

	# Determine genres to add and remove
	genre_ids_to_add = updated_genre_ids - current_user_genre_ids
	genre_ids_to_remove = current_user_genre_ids - updated_genre_ids

	# Query and add new genres
	if genre_ids_to_add:
		genres_to_add = db.query(Genre).filter(Genre.id.in_(genre_ids_to_add)).all()
		user.genres.extend(genres_to_add)

	# Remove genres that are no longer desired
	if genre_ids_to_remove:
		genres_to_remove = db.query(Genre).filter(Genre.id.in_(genre_ids_to_remove)).all()
		for genre in genres_to_remove:
			user.genres.remove(genre)

	db.commit()

	return {
		"message": "User genres updated.",
		"genre_ids_added": list(genre_ids_to_add),
		"genre_ids_removed": list(genre_ids_to_remove)
	}