from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.connections import init_db
from app.routers import restaurants, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()

    yield


app = FastAPI(lifespan=lifespan)

app.include_router(restaurants.router)
app.include_router(users.router)
