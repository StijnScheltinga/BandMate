from app.models import User, Genre
from fastapi import APIRouter, status
from app.router.auth import user_dependency
from app.database import db_dependency

router = APIRouter(
	prefix='/genre',
	tags=['genre']
)

@router.get("/user", status_code=status.HTTP_200_OK)
async def get_all_genres(user: user_dependency, db: db_dependency):
	genres = user.genres
	return genres

@router.get("/all", status_code=status.HTTP_200_OK)
async def get_all_genres(user: user_dependency, db: db_dependency):
	genres = db.query(Genre).all()
	return genres