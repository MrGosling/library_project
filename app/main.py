from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.api import api_router
from app.core import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title='Electronic Library API', lifespan=lifespan)
app.include_router(api_router, prefix='/api/v1')


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}
