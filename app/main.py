from fastapi import FastAPI, status
from app.database import engine
from app import models
from app.router import auth, user, genre, instrument, filter, profile
from app.scripts.startup import populate_initial_data
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
	models.Base.metadata.create_all(bind=engine)
	populate_initial_data()
	yield

app = FastAPI(lifespan=lifespan)


@app.get('/health', status_code=status.HTTP_200_OK)
def health_check():
	return {'status': 'Server is running'}

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(profile.router)
app.include_router(genre.router)
app.include_router(instrument.router)
app.include_router(filter.router)


