from fastapi import FastAPI
from app.database import engine
from app import models
from app.router import user

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(user.router)

from app.util.location import haversine

print(haversine(52.5200, 13.4050, 48.8566, 2.3522))

