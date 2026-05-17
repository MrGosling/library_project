from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.routers import main_router
from backend.core.config import settings
from backend.core.init_db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title=settings.title, lifespan=lifespan)

app.include_router(main_router)
