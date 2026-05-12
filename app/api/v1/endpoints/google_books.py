from typing import Any

from fastapi import APIRouter, Query

from app.integrations.google_books.service import google_books_service

router = APIRouter()


@router.get(
    path='/',
    summary='Поиск книг в Google Books',
    description='Позволяет искать книги через Google Books API по заданной строке запроса.',
)
async def search_google_books(
    query: str = Query(..., description='Строка запроса для поиска книг')
) -> dict[str, Any]:
    """
    Поиск книг с использованием Google Books API.
    """
    result = await google_books_service.search_books(query)
    return result
