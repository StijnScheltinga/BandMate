from app.models import Instrument
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

@router.post("/user/add", status_code=status.HTTP_201_CREATED)
async def add_instrument_to_user(user: user_dependency, db: db_dependency, user_instrument_update: UserInstrumentUpdate):
	existing_instrument_ids = {instrument.id for instrument in user.instruments}

	instruments_to_add = (
		db.query(Instrument)
		.filter(Instrument.id.in_(user_instrument_update.instrument_ids))
		.filter(~Instrument.id.in_(existing_instrument_ids))
		.all()
	)

	if not instruments_to_add:
		return {"message": "No new instruments to add."}

	user.instruments.extend(instruments_to_add)
	db.commit()

	return {
        "message": f"Added {len(instruments_to_add)} new instruments to user.",
        "instrument_ids_added": [instrument.id for instrument in instruments_to_add],
    }

@router.get("/user", status_code=status.HTTP_200_OK, response_model=List[InstrumentOut])
async def get_user_instruments(user: user_dependency, db: db_dependency):
	instruments = user.instruments
	return instruments

@router.get("/all", status_code=status.HTTP_200_OK, response_model=List[InstrumentOut])
async def get_all_instruments(user: user_dependency, db: db_dependency):
	instruments = db.query(Instrument).all()
	return instruments

@router.delete("/user/delete", status_code=status.HTTP_204_NO_CONTENT)
async def remove_instrument_from_user(user: user_dependency, db: db_dependency, user_instrument_update: UserInstrumentUpdate):
	current_user_instrument_ids = {instrument.id for instrument in user.instruments}

	instrument_ids_to_remove = current_user_instrument_ids & set(user_instrument_update.instrument_ids)

	if not instrument_ids_to_remove:
		raise HTTPException(status_code=404, detail="Can only delete instruments currently assigned to user")

	instruments_to_remove = db.query(Instrument).filter(Instrument.id.in_(instrument_ids_to_remove)).all()

	for instrument in instruments_to_remove:
		user.instruments.remove(instrument)
	
	db.commit()