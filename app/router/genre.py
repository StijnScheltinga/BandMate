from app.models import Genre
from fastapi import APIRouter, status, HTTPException
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

class GenreOut(BaseModel):
	id: int
	name: str

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

@router.get("/user", status_code=status.HTTP_200_OK, response_model=List[GenreOut])
async def get_user_genres(user: user_dependency, db: db_dependency):
	genres = user.genres
	return genres

@router.get("/all", status_code=status.HTTP_200_OK, response_model=List[GenreOut])
async def get_all_genres(user: user_dependency, db: db_dependency):
	genres = db.query(Genre).all()
	return genres


@router.delete("/user/delete", status_code=status.HTTP_204_NO_CONTENT)
async def remove_genre_from_user(user: user_dependency, db: db_dependency, user_genre_update: UserGenreUpdate):
	current_user_genre_ids = {genre.id for genre in user.genres}

	genre_ids_to_remove = current_user_genre_ids & set(user_genre_update.genre_ids)

	if not genre_ids_to_remove:
		raise HTTPException(status_code=404, detail="Can only delete genres currently assigned to user")

	genres_to_remove = db.query(Genre).filter(Genre.id.in_(genre_ids_to_remove)).all()

	for genre in genres_to_remove:
		user.genres.remove(genre)
	
	db.commit()