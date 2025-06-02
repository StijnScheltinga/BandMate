from fastapi import APIRouter, status, HTTPException
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
	if user.latitude is None or user.longitude is None:
		raise HTTPException(status_code=400, detail='User has no location specified')

	users = (
		db.query(User)
		.filter(User.latitude.isnot(None))
		.filter(User.longitude.isnot(None))
		.filter(User.id != user.id)
		.all()
	)
	users_with_distance = []

	for other_user in users:
		distance = haversine(other_user.latitude, other_user.longitude, user.latitude, user.longitude)
		other_user.distance_km = round(distance, 2)
		print(other_user.distance_km)
		users_with_distance.append(other_user)
	
	users_with_distance.sort(key=lambda user: user.distance_km)

	return users_with_distance