from fastapi import APIRouter, status
from app.database import db_dependency
from app.router.auth import user_dependency
from app.router.user import UserOut 
from app.models import User
from app.util.location import haversine
from typing import List

router = APIRouter(
	prefix="/filter",
	tags=["filter"]
)


@router.get("/location", status_code=status.HTTP_200_OK, response_model=List[UserOut])
async def filter_by_location(user: user_dependency, db: db_dependency):
	users = (
		db.query(User)
		.filter(User.latitude is not None)
		.filter(User.longitude is not None)
		.filter(User.id != user.id)
		.all()
	)
	# users_with_distance = [
	# 	UserOut()
	# 	for u in users
	# ]

	return users