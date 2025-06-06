from fastapi import APIRouter, status, HTTPException
from app.router.user import User, user_dependency, UserOut
from app.database import db_dependency
from app.router.band import Band, BandOut
from app.models import BandInvite
from pydantic import BaseModel
from sqlalchemy.exc import IntegrityError
from typing import List
from enum import Enum

router = APIRouter(
	prefix='/invites',
	tags=['invites']
)

class InviteAction(str, Enum):
	accept = "accept"
	decline = "decline"

class SendInvite(BaseModel):
	band_id: int
	user_ids: List[int]

class ResponseInvite(BaseModel):
	invite_id: int
	action: InviteAction

class BandInviteOut(BaseModel):
	id: int
	status: str
	band: BandOut
	sender: UserOut
	reciever: UserOut

@router.post('/invite', status_code=status.HTTP_200_OK)
async def invite_user(user: user_dependency, db: db_dependency, user_invite: SendInvite):
	band_id = user_invite.band_id

	# Perform a query for a band where the id is equal to the request and user is in said band
	band = (
		db.query(Band)
		.join(Band.users)
		.filter(Band.id == band_id)
		.filter(User.id == user.id)
		.first()
	)

	if not band:
		raise HTTPException(status_code=404, detail="band not found or user not in band")
	
	member_user_ids = {member.id for member in band.users}
	
	for user_to_invite_id in user_invite.user_ids:

		# Check if the user to invite is not already in the band
		if user_to_invite_id in member_user_ids:
			raise HTTPException(status_code=400, detail=f"User {user_to_invite_id} is already in the band")

		invite = BandInvite(
			band_id = band_id,
			sender_id = user.id,
			reciever_id = user_to_invite_id
		)
		db.add(invite)
		# Check for unique constraint
		try:
			db.commit()
		except IntegrityError as e:
			db.rollback()
			raise HTTPException(status_code=400, detail="invite already sent")

	n_users_invited = len(user_invite.user_ids)

	return {
		"message": f"Invited {n_users_invited} users to join {band.name}"
	}

@router.post('/respond', status_code=status.HTTP_200_OK)
async def accept_or_decline_invite(user: user_dependency, db: db_dependency, response: ResponseInvite):
	if response.action not in ["accept", "decline"]:
		raise HTTPException(status_code=400, detail="Can only accept or decline invite")
	
	band_invite = (
		db.query(BandInvite)
		.filter(BandInvite.id == response.invite_id)
		.first()
	)
	if not band_invite:
		raise HTTPException(status_code=404, detail='band invite not found')
	
	if band_invite.reciever != user:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Can only accept or decline invites belonging to user")

	if band_invite.status != "pending":
		raise HTTPException(status_code=400, detail="Cannot accept or decline already finished invite")

	band = band_invite.band

	if response.action == "accept":
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

@router.get('/invites/incoming', status_code=status.HTTP_200_OK, response_model=List[BandInviteOut])
async def get_user_incoming_invites(user: user_dependency):
	pending_invites = [invite for invite in user.incoming_invites if invite.status == "pending"]
	return pending_invites

@router.get('/invites/outgoing', status_code=status.HTTP_200_OK, response_model=List[BandInviteOut])
async def get_user_outgoing_invites(user: user_dependency):
	pending_invites = [invite for invite in user.outgoing_invites if invite.status == "pending"]
	return pending_invites