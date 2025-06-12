from fastapi import FastAPI, status
from app.database import engine, get_db
from app import models
from app.config import settings
from app.router import auth, user, genre, instrument, filter, profile, band, invites
from app.scripts.startup import populate_initial_data
from contextlib import asynccontextmanager
from pydantic import BaseModel
import sentry_sdk

@asynccontextmanager
async def lifespan(app: FastAPI):
	models.Base.metadata.create_all(bind=engine)
	populate_initial_data(get_db)
	yield

sentry_sdk.init(
	dsn="https://84c7185b7c284169d5bce1798aee3227@o4507723857526784.ingest.de.sentry.io/4509451296702544",
	send_default_pii=True,
	environment=settings.ENVIRONMENT
)

app = FastAPI(lifespan=lifespan)

class HealthOut(BaseModel):
	status: dict = 'Server is running'

@app.get('/health', status_code=status.HTTP_200_OK)
def health_check():
	return {'status': 'Server is running'}

@app.get('/sentry_debug')
async def trigger_error():
	division_by_zero = 1 / 0

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(profile.router)
app.include_router(genre.router)
app.include_router(instrument.router)
app.include_router(filter.router)
app.include_router(band.router)
app.include_router(invites.router)


