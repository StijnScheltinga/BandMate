from fastapi import FastAPI
from app.database import engine
from app import models
from app.router import auth, user
from app.scripts.startup import populate_initial_data
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    populate_initial_data()
    yield

app = FastAPI(lifespan=lifespan)

models.Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(user.router)


