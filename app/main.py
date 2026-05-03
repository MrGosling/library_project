from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core import init_db

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_async_session
from app.models.user import User
from app.schemas.user import UserRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="Electronic Library API", lifespan=lifespan)
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/api/v1/users", response_model=list[UserRead])
async def get_users(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(User))
    users = result.scalars().all()
    return users