from fastapi import APIRouter, status, File, UploadFile, HTTPException
from app.database import db_dependency
from app.router.auth import user_dependency
from app.models import Genre, Instrument, Media
from pydantic import BaseModel
from typing import List
from azure.storage.blob import BlobServiceClient
from app.config import settings
from datetime import datetime, timezone

BLOB_CONNECTION_STRING = settings.BLOB_CONNECTION_STRING
CONTAINER_NAME = settings.CONTAINER_NAME
blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(CONTAINER_NAME)

router = APIRouter(
	prefix='/profile',
	tags=['profile']
)

class ProfileInfo(BaseModel):
	display_name: str
	genre_ids: List[int]
	instrument_ids: List[int]
	latitude: float
	longitude: float

	class Config:
		json_schema_extra = {
			"example": {
				"display_name": "user123",
				"genre_ids": [1, 3, 19],
				"instrument_ids": [4, 7, 13],
				"latitude": 52.719474,
				"longitude": 5.075181
			}
		}

class MediaOut(BaseModel):
	blob_url: str

@router.post('/setup', status_code=status.HTTP_201_CREATED)
async def set_profile_info(user: user_dependency, db: db_dependency, profile_info: ProfileInfo):

	genres_to_add = db.query(Genre).filter(Genre.id.in_(profile_info.genre_ids)).all()
	user.genres.extend(genres_to_add)

	instruments_to_add = db.query(Instrument).filter(Instrument.id.in_(profile_info.instrument_ids)).all()
	user.instruments.extend(instruments_to_add)

	user.display_name = profile_info.display_name
	user.latitude = profile_info.latitude
	user.longitude = profile_info.longitude

	db.commit()

@router.post('/upload', status_code=status.HTTP_200_OK)
async def upload_user_media(user: user_dependency, db: db_dependency, file: UploadFile):
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
	
	return {"url": blob_url}

@router.get('/media', status_code=status.HTTP_200_OK, response_model=List[MediaOut])
async def get_profile_media(user: user_dependency):
	return user.media

@router.get('/default/avatar', status_code=status.HTTP_200_OK, response_model=List[str])
async def get_default_avatars():
	container_client = blob_service_client.get_container_client("default-avatar")
	blob_list = container_client.list_blobs()
	urls = [f"https://{blob_service_client.account_name}.blob.core.windows.net/default-avatar/{blob.name}" for blob in blob_list]
	return urls