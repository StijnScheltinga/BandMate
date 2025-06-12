from app.models import Instrument
from app.scripts.startup import INSTRUMENTS
from fastapi import APIRouter, status, HTTPException
from app.router.auth import user_dependency
from app.database import db_dependency
from typing import List
from pydantic import BaseModel

router = APIRouter(
	prefix='/instrument',
	tags=['instrument']
)

class UserInstrumentUpdate(BaseModel):
	instrument_ids: List[int]

class InstrumentOut(BaseModel):
	id: int
	name: str

@router.get("/all", status_code=status.HTTP_200_OK, response_model=List[InstrumentOut])
async def get_all_instruments(user: user_dependency, db: db_dependency):
	instruments = db.query(Instrument).all()
	return instruments

@router.get("/user", status_code=status.HTTP_200_OK, response_model=List[InstrumentOut])
async def get_user_instruments(user: user_dependency, db: db_dependency):
	instruments = user.instruments
	return instruments

@router.put("/user", status_code=status.HTTP_200_OK)
async def update_instruments_user(user: user_dependency, db: db_dependency, user_instrument_update: UserInstrumentUpdate):
	"""
	Logic for updating: 
	instrument in update and in current, do nothing
	instrument in update not in current, add
	Instrument not in update in current, remove
	"""
	current_user_instrument_ids = {instrument.id for instrument in user.instruments}

	# Get instrument IDs from the request payload
	updated_instrument_ids = set(user_instrument_update.instrument_ids)

	# Check if the incoming ID's are valid
	instruments = db.query(Instrument).all()
	instrument_ids_in_database = [instrument.id for instrument in instruments]
	
	for g_id in updated_instrument_ids:
		if g_id not in instrument_ids_in_database:
			raise HTTPException(status_code=404, detail=f"Id {g_id} does not exist")


	# Determine instruments to add and remove
	instrument_ids_to_add = updated_instrument_ids - current_user_instrument_ids
	instrument_ids_to_remove = current_user_instrument_ids - updated_instrument_ids

	# Query and add new instruments
	if instrument_ids_to_add:
		instruments_to_add = db.query(Instrument).filter(Instrument.id.in_(instrument_ids_to_add)).all()
		user.instruments.extend(instruments_to_add)

	# Remove instruments that are no longer desired
	if instrument_ids_to_remove:
		instruments_to_remove = db.query(Instrument).filter(Instrument.id.in_(instrument_ids_to_remove)).all()
		for instrument in instruments_to_remove:
			user.instruments.remove(instrument)

	db.commit()

	return {
		"message": "User instruments updated.",
		"instrument_ids_added": list(instrument_ids_to_add),
		"instrument_ids_removed": list(instrument_ids_to_remove)
	}
