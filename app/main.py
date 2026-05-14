from fastapi import FastAPI

from app.api.routers import main_router
from app.core.config import settings
from app.api.endpoints import user

app = FastAPI(title=settings.title)

app.include_router(main_router)
app.include_router(user.router, prefix="/api/v1")
