from fastapi import APIRouter

from backend.api.v1.endpoints.ai import router as ai_router
from backend.api.v1.endpoints.authors import router as authors_router
from backend.api.v1.endpoints.books import router as books_router
from backend.api.v1.endpoints.categories import router as categories_router
from backend.api.v1.endpoints.genres import router as genres_router
from backend.api.v1.endpoints.google_books import router as google_books_router
from backend.api.v1.endpoints.health import router as health_router
from backend.api.v1.endpoints.users import router as users_router
from backend.api.v1.endpoints.reviews import router as reviews_router
from backend.api.v1.endpoints.favorites import router as favorites_router

endpoints_router = APIRouter()

endpoints_router.include_router(
    authors_router, prefix='/authors', tags=['Authors']
)
endpoints_router.include_router(books_router, prefix='/books', tags=['Books'])
endpoints_router.include_router(
    categories_router, prefix='/categories', tags=['Categories']
)
endpoints_router.include_router(
    genres_router, prefix='/genres', tags=['Genres']
)
endpoints_router.include_router(
    google_books_router, prefix='/google_books', tags=['Google Books']
)
endpoints_router.include_router(health_router)
endpoints_router.include_router(users_router, prefix='/users', tags=['Users'])
endpoints_router.include_router(ai_router)
endpoints_router.include_router(reviews_router, prefix='/reviews', tags=['Reviews'])
endpoints_router.include_router(favorites_router, prefix='/favorites', tags=['Favorites'])
