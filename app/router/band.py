from fastapi import APIRouter, status, HTTPException
from app.router.user import user_dependency, UserOut, User
from app.database import db_dependency
from app.models import Band, BandInvite
from sqlalchemy.exc import IntegrityError
from pydantic import BaseModel
from typing import List

router = APIRouter(
	prefix="/band",
	tags=["band"]
)

class BandCreationForm(BaseModel):
	name: str

class UserInvite(BaseModel):
	user_ids: List[int]

class BandOut(BaseModel):
	id: int
	name: str
	users: List[UserOut]

@router.post('/create', status_code=status.HTTP_204_NO_CONTENT)
async def create_band(user: user_dependency, db: db_dependency, band_creation_form: BandCreationForm):
	band = Band(
		name=band_creation_form.name
	)
	band.users.append(user)
	db.add(band)
	db.commit()

@router.get('/all', status_code=status.HTTP_200_OK, response_model=List[BandOut])
async def get_all_bands(user: user_dependency, db: db_dependency):
	bands = db.query(Band).all()
	return bands

@router.get('/user', status_code=status.HTTP_200_OK, response_model=List[BandOut])
async def get_user_bands(user: user_dependency, db: db_dependency):	
	return user.bands

@router.post('/{band_id}/invite', status_code=status.HTTP_200_OK)
async def invite_user(user: user_dependency, db: db_dependency, band_id: int, user_invite: UserInvite):
	band = db.query(Band).filter(Band.id == band_id).first()
	if not band:
		raise HTTPException(status_code=400, detail="Band not found")
	
	for user_to_invite_id in user_invite.user_ids:
		# Check if the user to invite is not already in the band (needs to be implemented)

		invite = BandInvite(
			band_id = band_id,
			sender_id = user.id,
			reciever_id = user_to_invite_id
		)
		db.add(invite)
		try:
			db.commit()
		except IntegrityError as e:
			db.rollback()
			raise HTTPException(status_code=400, detail="invite already sent")

	n_users_invited = len(user_invite.user_ids)

	return {
		"message": f"Invited {n_users_invited} users to join {band.name}"
	}