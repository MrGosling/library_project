from fastapi import APIRouter

from app.api.v1.endpoints.authors import router as authors_router
from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.genres import router as genres_router
from app.api.v1.endpoints.google_books import router as google_books_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.users import router as users_router

endpoints_router = APIRouter()

endpoints_router.include_router(authors_router, prefix='/authors', tags=['Authors'])
endpoints_router.include_router(categories_router, prefix='/categories', tags=['Categories'])
endpoints_router.include_router(genres_router, prefix='/genres', tags=['Genres'])
endpoints_router.include_router(google_books_router, prefix='/google_books', tags=['Google Books'])
endpoints_router.include_router(health_router)
endpoints_router.include_router(users_router, prefix='/users', tags=['Users'])
