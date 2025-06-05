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

class SendInvite(BaseModel):
	user_ids: List[int]

class RespondInvite(BaseModel):
	status: str

class BandOut(BaseModel):
	id: int
	name: str
	users: List[UserOut]

class BandInviteOut(BaseModel):
	id: int
	status: str
	band: BandOut
	sender: UserOut
	reciever: UserOut

@router.post('/create', status_code=status.HTTP_204_NO_CONTENT)
async def create_band(user: user_dependency, db: db_dependency, band_creation_form: BandCreationForm):
	band = Band(
		name=band_creation_form.name
	)
	band.users.append(user)
	db.add(band)
	db.commit()

@router.post('/{band_id}/invite', status_code=status.HTTP_200_OK)
async def invite_user(user: user_dependency, db: db_dependency, band_id: int, user_invite: SendInvite):
	
	band = (
		db.query(Band)
		.join(Band.users)
		.filter(Band.id == band_id)
		.filter(User.id == user.id)
		.first()
	)

	if not band:
		raise HTTPException(status_code=404, detail="band not found or user not in band")
	
	for user_to_invite_id in user_invite.user_ids:
		# Check if the user to invite is not already in the band (needs to be implemented)
		for member in band.users:
			if user_to_invite_id == member.id:
				raise HTTPException(status_code=400, detail=f"User {member.id} is already in the band")

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

@router.get('/all', status_code=status.HTTP_200_OK, response_model=List[BandOut])
async def get_all_bands(user: user_dependency, db: db_dependency):
	bands = db.query(Band).all()
	return bands

@router.get('/user', status_code=status.HTTP_200_OK, response_model=List[BandOut])
async def get_user_bands(user: user_dependency, db: db_dependency):	
	return user.bands

@router.get('/invites/incoming', status_code=status.HTTP_200_OK, response_model=List[BandInviteOut])
async def get_user_incoming_invites(user: user_dependency, db: db_dependency):
	pending_invites = [invite for invite in user.incoming_invites if invite.status == "pending"]
	return pending_invites

@router.get('/invites/outgoing', status_code=status.HTTP_200_OK, response_model=List[BandInviteOut])
async def get_user_outgoing_invites(user: user_dependency):
	pending_invites = [invite for invite in user.outgoing_invites if invite.status == "pending"]
	return pending_invites

@router.post('/{invite_id}/{action}', status_code=status.HTTP_200_OK)
async def accept_or_decline_invite(user: user_dependency, db: db_dependency, invite_id: int, action: str):
	if action not in ["accept", "decline"]:
		raise HTTPException(status_code=400, detail="Can only accept or decline invite")
	
	band_invite = (
		db.query(BandInvite)
		.filter(BandInvite.id == invite_id)
		.first()
	)
	if not band_invite:
		raise HTTPException(status_code=404, detail='band invite not found')
	
	if band_invite.reciever != user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Can only accept or decline invites belonging to user")

	if band_invite.status != "pending":
		raise HTTPException(status_code=400, detail="Cannot accept or decline already finished invite")

	band = band_invite.band

	if action == "accept":
		band.users.append(user)
		band_invite.status = "accepted"
		db.commit()
		return {
			"message": f"user has accepted invitation of {band_invite.sender.display_name} to join {band.name}",
		}
	else:
		band_invite.status = "declined"
		db.commit()
		return {
			"message": f"user has declined invitation of {band_invite.sender.display_name} to join {band.name}"
		}
