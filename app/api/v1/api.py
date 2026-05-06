from fastapi import APIRouter

from app.api.v1.endpoints import categories, genres, users

api_router = APIRouter()
api_router.include_router(authors.router, prefix='/authors', tags=['authors'])
api_router.include_router(users.router, prefix='/users', tags=['users'])
api_router.include_router(genres.router, prefix='/genres', tags=['genres'])
api_router.include_router(categories.router, prefix='/categories', tags=['categories'])
