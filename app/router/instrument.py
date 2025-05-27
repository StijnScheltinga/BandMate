from app.models import Instrument
from fastapi import APIRouter, status
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

@router.get("/user", status_code=status.HTTP_200_OK, response_model=List[InstrumentOut])
async def get_user_instruments(user: user_dependency, db: db_dependency):
	instruments = user.instruments
	return instruments

@router.get("/all", status_code=status.HTTP_200_OK, response_model=List[InstrumentOut])
async def get_all_instruments(user: user_dependency, db: db_dependency):
	instruments = db.query(Instrument).all()
	return instruments

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