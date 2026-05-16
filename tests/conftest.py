from collections.abc import AsyncIterator
from typing import TypeVar

import httpx
import pytest_asyncio
from fastapi import FastAPI

from app.api.v1.endpoints.books import router as books_router
from app.api.v1.endpoints.categories import router as categories_router
from app.api.v1.endpoints.genres import router as genres_router
from app.core.db import get_async_session
from app.models.author import Author
from app.models.book import Book
from app.models.category import Category
from app.models.genre import Genre

ModelT = TypeVar('ModelT', Author, Book, Category, Genre)


class FakeScalarResult:
    def __init__(self, items: list[Author] | list[Book] | list[Category] | list[Genre]) -> None:
        self.items = items

    def all(self) -> list[Author] | list[Book] | list[Category] | list[Genre]:
        return self.items


class FakeResult:
    def __init__(self, items: list[Author] | list[Book] | list[Category] | list[Genre]) -> None:
        self.items = items

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self.items)

    def scalar_one_or_none(self) -> Author | Book | Category | Genre | None:
        if not self.items:
            return None
        return self.items[0]


class FakeLibrarySession:
    def __init__(self) -> None:
        self.authors: list[Author] = [self._build_author(author_id=1)]
        self.books: list[Book] = []
        self.categories: list[Category] = []
        self.genres: list[Genre] = []
        self._next_ids: dict[type[Author] | type[Book] | type[Category] | type[Genre], int] = {
            Author: 2,
            Book: 1,
            Category: 1,
            Genre: 1,
        }

    async def execute(self, statement) -> FakeResult:
        model = statement.column_descriptions[0]['entity']
        items = list(self._items_for(model))

        if statement.whereclause is not None:
            expected_name = next(iter(statement.compile().params.values()))
            items = [item for item in items if item.name == expected_name]

        return FakeResult(items)

    async def get(self, model: type[ModelT], item_id: int) -> ModelT | None:
        return next((item for item in self._items_for(model) if item.id == item_id), None)

    def add(self, item: Author | Book | Category | Genre) -> None:
        model = type(item)
        item.id = self._next_ids[model]
        self._next_ids[model] += 1
        self._items_for(model).append(item)

    async def commit(self) -> None:
        return None

    async def refresh(self, item: Author | Book | Category | Genre) -> None:
        return None

    async def delete(self, item: Author | Book | Category | Genre) -> None:
        self._items_for(type(item)).remove(item)

    def _items_for(self, model: type[ModelT]) -> list[ModelT]:
        if model is Author:
            return self.authors
        if model is Book:
            return self.books
        if model is Category:
            return self.categories
        if model is Genre:
            return self.genres
        raise TypeError(f'Unsupported model: {model!r}')

    @staticmethod
    def _build_author(author_id: int) -> Author:
        author = Author(full_name='Тестовый автор', birth_year=1990, bio=None)
        author.id = author_id
        return author


@pytest_asyncio.fixture
async def async_client() -> AsyncIterator[httpx.AsyncClient]:
    app = FastAPI()
    app.include_router(books_router, prefix='/api/v1/books')
    app.include_router(categories_router, prefix='/api/v1/categories')
    app.include_router(genres_router, prefix='/api/v1/genres')

    fake_session = FakeLibrarySession()

    async def override_get_async_session() -> AsyncIterator[FakeLibrarySession]:
        yield fake_session

    app.dependency_overrides[get_async_session] = override_get_async_session

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as client:
        yield client
