from datetime import datetime, timezone
from collections.abc import AsyncIterator
from typing import TypeVar, Any

import httpx
import pytest_asyncio
from fastapi import FastAPI

from backend.api.v1.endpoints.books import router as books_router
from backend.api.v1.endpoints.categories import router as categories_router
from backend.api.v1.endpoints.genres import router as genres_router
from backend.api.v1.endpoints.authors import router as authors_router
from backend.api.v1.endpoints.users import router as users_router
from backend.api.v1.endpoints.ai import router as ai_router
from backend.core.db import get_async_session
from backend.models.author import Author
from backend.models.book import Book
from backend.models.category import Category
from backend.models.genre import Genre
from backend.models.user import User

ModelT = TypeVar('ModelT', Author, Book, Category, Genre, User)


class FakeScalarResult:
    def __init__(self, items: list[Any]) -> None:
        self.items = items

    def all(self) -> list[Any]:
        return self.items

    def first(self) -> Any | None:
        return self.items[0] if self.items else None


class FakeResult:
    def __init__(self, items: list[Any]) -> None:
        self.items = items

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self.items)

    def scalar_one_or_none(self) -> Any | None:
        if not self.items:
            return None
        return self.items[0]


class FakeLibrarySession:
    def __init__(self) -> None:
        self.authors: list[Author] = [self._build_author(author_id=1)]
        self.books: list[Book] = []
        self.categories: list[Category] = []
        self.genres: list[Genre] = []
        self.users: list[User] = []
        self._next_ids: dict[type, int] = {
            Author: 2,
            Book: 1,
            Category: 1,
            Genre: 1,
            User: 1,
        }

    async def execute(self, statement) -> FakeResult:
        model = statement.column_descriptions[0]['entity']
        items = list(self._items_for(model))

        if hasattr(statement, 'whereclause') and statement.whereclause is not None:
            params = statement.compile().params
            for key, value in params.items():
                if 'username' in key:
                    items = [i for i in items if i.username == value]
                elif 'email' in key:
                    items = [i for i in items if i.email == value]
                elif 'name' in key:
                    items = [i for i in items if i.name == value]
                elif 'full_name' in key:
                    items = [i for i in items if value.lower() in i.full_name.lower()]

        return FakeResult(items)

    async def get(self, model: type[ModelT], item_id: int) -> ModelT | None:
        return next(
            (item for item in self._items_for(model) if item.id == item_id),
            None,
        )

    def add(self, item: Any) -> None:
        model = type(item)
        now = datetime.now(timezone.utc)
        
        if not hasattr(item, 'id') or item.id is None:
            item.id = self._next_ids.get(model, 1)
            self._next_ids[model] = self._next_ids.get(model, 1) + 1
            
        if hasattr(item, 'created_at') and item.created_at is None:
            item.created_at = now
        if hasattr(item, 'updated_at') and item.updated_at is None:
            item.updated_at = now
        if hasattr(item, 'is_superuser') and item.is_superuser is None:
            item.is_superuser = False
        if hasattr(item, 'is_active') and item.is_active is None:
            item.is_active = True

        self._items_for(model).append(item)

    async def commit(self) -> None:
        pass

    async def refresh(self, item: Any) -> None:
        pass

    async def delete(self, item: Any) -> None:
        self._items_for(type(item)).remove(item)

    def _items_for(self, model: type) -> list[Any]:
        if model is Author:
            return self.authors
        if model is Book:
            return self.books
        if model is Category:
            return self.categories
        if model is Genre:
            return self.genres
        if model is User:
            return self.users
        raise TypeError(f'Unsupported model: {model!r}')

    @staticmethod
    def _build_author(author_id: int) -> Author:
        now = datetime.now(timezone.utc)
        author = Author(full_name='Тестовый автор', birth_year=1990, bio=None)
        author.id = author_id
        author.created_at = now
        author.updated_at = now
        return author


@pytest_asyncio.fixture
async def async_client() -> AsyncIterator[httpx.AsyncClient]:
    app = FastAPI()
    # Добавляем слеш в конце, чтобы избежать 307 Redirect, 
    # так как многие роутеры FastAPI по умолчанию ожидают /
    app.include_router(books_router, prefix='/api/v1/books')
    app.include_router(categories_router, prefix='/api/v1/categories')
    app.include_router(genres_router, prefix='/api/v1/genres')
    app.include_router(authors_router, prefix='/api/v1/authors')
    app.include_router(users_router, prefix='/api/v1/users')
    app.include_router(ai_router, prefix='/api/v1/ai')

    fake_session = FakeLibrarySession()

    async def override_get_async_session() -> AsyncIterator[FakeLibrarySession]:
        yield fake_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url='http://test', follow_redirects=True
    ) as client:
        yield client
