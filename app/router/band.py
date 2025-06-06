from fastapi import APIRouter, status
from app.router.user import user_dependency, UserOut
from app.database import db_dependency
from app.models import Band
from pydantic import BaseModel
from typing import List

router = APIRouter(
	prefix="/band",
	tags=["band"]
)

class BandCreationForm(BaseModel):
	name: str

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