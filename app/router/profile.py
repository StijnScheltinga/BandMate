from fastapi import APIRouter, status, File, UploadFile, HTTPException
from app.database import db_dependency
from app.router.auth import user_dependency
from app.models import Genre, Instrument, Media
from pydantic import BaseModel
from typing import List
from azure.storage.blob import BlobServiceClient
from app.config import settings
from datetime import datetime, timezone
from app.util.location import get_city_from_latlong

BLOB_CONNECTION_STRING = settings.BLOB_CONNECTION_STRING
CONTAINER_NAME = settings.CONTAINER_NAME
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

router = APIRouter(
	prefix='/profile',
	tags=['profile']
)

class ProfileSetup(BaseModel):
	display_name: str
	genre_ids: List[int]
	instrument_ids: List[int]
	latitude: float
	longitude: float
	profile_picture: str

	class Config:
		json_schema_extra = {
			"example": {
				"display_name": "user123",
				"genre_ids": [1, 3, 19],
				"instrument_ids": [4, 7, 13],
				"latitude": 52.719474,
				"longitude": 5.075181,
				"profile_picture": "https://bandmate.blob.core.windows.net/default-avatar/guitarist.png"
			}
		}

class MediaOut(BaseModel):
	blob_url: str

# Should remake with optional parameters
class ProfileOut(ProfileSetup):

	media: List[MediaOut]

	class Config:
		json_schema_extra = {
			"example": {
				"display_name": "user123",
				"genre_ids": [1, 3, 19],
				"instrument_ids": [4, 7, 13],
				"latitude": 52.719474,
				"longitude": 5.075181,
				"profile_picture": "https://bandmate.blob.core.windows.net/default-avatar/guitarist.png",
				"media": [
					"https://bandmate.blob.core.windows.net/default-avatar/guitarist.png",
					"https://bandmate.blob.core.windows.net/1/image.png",
					"https://bandmate.blob.core.windows.net/1/video.mp4"
				]
			}
		}


@router.post('/setup', status_code=status.HTTP_201_CREATED)
async def set_profile_info(user: user_dependency, db: db_dependency, profile_info: ProfileSetup):
	if user.setup_complete:
		raise HTTPException(status_code=400, detail="User has already completed setup")

	genres_to_add = db.query(Genre).filter(Genre.id.in_(profile_info.genre_ids)).all()
	user.genres.extend(genres_to_add)

	instruments_to_add = db.query(Instrument).filter(Instrument.id.in_(profile_info.instrument_ids)).all()
	user.instruments.extend(instruments_to_add)

	user.display_name = profile_info.display_name
	user.latitude = profile_info.latitude
	user.longitude = profile_info.longitude
	user.profile_picture = profile_info.profile_picture
	user.city = get_city_from_latlong(user.latitude, user.longitude)

	user.setup_complete = True

	db.commit()

@router.post('/upload', status_code=status.HTTP_200_OK, response_model=List[str])
async def upload_user_media(user: user_dependency, db: db_dependency, media: List[UploadFile]):
	urls = []

	for file in media:
		timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')
		filename = f"{timestamp}_{file.filename}"
		blob_path = f"{str(user.id)}/{filename}"

		blob_client = container_client.get_blob_client(blob_path)
		try:
			data = await file.read()
			blob_client.upload_blob(data, overwrite=True)
		except Exception as e:
			raise HTTPException(status_code=500, detail=str(e))
		
		blob_url = f"https://{blob_service_client.account_name}.blob.core.windows.net/{CONTAINER_NAME}/{blob_path}"

		media_entry = Media(user_id=user.id, blob_url=blob_url)
		db.add(media_entry)
		db.commit()

		urls.append(blob_url)
	
	return {"blob_urls": urls}

@router.get('', status_code=status.HTTP_200_OK, response_model=ProfileOut)
async def get_profile(user: user_dependency):
	return user

@router.get('/default/avatar', status_code=status.HTTP_200_OK, response_model=List[str])
async def get_default_avatars():
	container_client = blob_service_client.get_container_client("default-avatar")
	blob_list = container_client.list_blobs()
	urls = [f"https://{blob_service_client.account_name}.blob.core.windows.net/default-avatar/{blob.name}" for blob in blob_list]
	return urls

# Needs an endpoint for changing user profile info also for debugging latlong to city
