import re
from collections.abc import AsyncIterator

import httpx
import pytest
import pytest_asyncio
from fastapi import FastAPI

from backend.api.v1.endpoints.books import router as books_router
from backend.core.db import get_async_session
from backend.models.book import Book


class FakeScalarResult:
    def __init__(self, items: list[Book]) -> None:
        self.items = items

    def all(self) -> list[Book]:
        return self.items


class FakeResult:
    def __init__(self, items: list[Book]) -> None:
        self.items = items

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self.items)


class FakeFilterSession:
    def __init__(self) -> None:
        self.books: list[Book] = [
            self._make(1, 'Война и мир', 1869, author_id=1),
            self._make(2, 'Анна Каренина', 1878, author_id=1),
            self._make(3, 'Преступление и наказание', 1866, author_id=2),
            self._make(4, 'Идиот', 1869, author_id=2),
            self._make(5, 'Мастер и Маргарита', 1967, author_id=3),
        ]

    @staticmethod
    def _make(book_id: int, title: str, pub_year: int, author_id: int) -> Book:
        book = Book(title=title, pub_year=pub_year, author_id=author_id)
        book.id = book_id
        return book

    async def execute(self, statement) -> FakeResult:
        params = statement.compile().params
        items = list(self.books)

        for key, value in params.items():
            if 'title' in key:
                search_term = str(value).strip('%').lower()
                items = [b for b in items if search_term in b.title.lower()]
            elif 'author_id' in key:
                items = [b for b in items if b.author_id == value]
            elif 'pub_year' in key:
                items = [b for b in items if b.pub_year == value]
            elif 'category_id' in key:
                items = []

        limit: int | None = None
        offset: int | None = None
        try:
            lc = getattr(statement, '_limit_clause', None)
            oc = getattr(statement, '_offset_clause', None)
            if lc is not None:
                limit = int(lc.value)
            if oc is not None:
                offset = int(oc.value)
        except (AttributeError, TypeError):
            from sqlalchemy.dialects import sqlite as sqlite_dialect
            sql = str(
                statement.compile(
                    dialect=sqlite_dialect.dialect(),
                    compile_kwargs={'literal_binds': True},
                )
            )
            lm = re.search(r'\bLIMIT\s+(\d+)', sql, re.IGNORECASE)
            om = re.search(r'\bOFFSET\s+(\d+)', sql, re.IGNORECASE)
            if lm:
                limit = int(lm.group(1))
            if om:
                offset = int(om.group(1))

        if offset:
            items = items[offset:]
        if limit is not None:
            items = items[:limit]

        return FakeResult(items)

    async def get(self, model: type, item_id: int) -> Book | None:
        return next((b for b in self.books if b.id == item_id), None)

    def add(self, item: Book) -> None:
        item.id = max((b.id for b in self.books), default=0) + 1
        self.books.append(item)

    async def commit(self) -> None:
        pass

    async def refresh(self, item: Book) -> None:
        pass

    async def delete(self, item: Book) -> None:
        self.books.remove(item)


@pytest_asyncio.fixture
async def filter_client() -> AsyncIterator[httpx.AsyncClient]:
    app = FastAPI()
    app.include_router(books_router, prefix='/api/v1/books')
    session = FakeFilterSession()

    async def override() -> AsyncIterator[FakeFilterSession]:
        yield session

    app.dependency_overrides[get_async_session] = override
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url='http://test') as client:
        yield client


@pytest.mark.asyncio
async def test_no_filters_returns_all_books(filter_client: httpx.AsyncClient) -> None:
    response = await filter_client.get('/api/v1/books', params={'limit': 100})
    assert response.status_code == 200
    assert len(response.json()) == 5


@pytest.mark.asyncio
async def test_filter_by_author_id(filter_client: httpx.AsyncClient) -> None:
    response = await filter_client.get('/api/v1/books', params={'author_id': 1, 'limit': 100})
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 2
    assert all(b['author_id'] == 1 for b in books)


@pytest.mark.asyncio
async def test_filter_by_author_id_returns_empty_for_unknown(filter_client: httpx.AsyncClient) -> None:
    response = await filter_client.get('/api/v1/books', params={'author_id': 999, 'limit': 100})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_filter_by_pub_year(filter_client: httpx.AsyncClient) -> None:
    response = await filter_client.get('/api/v1/books', params={'pub_year': 1869, 'limit': 100})
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 2
    assert all(b['pub_year'] == 1869 for b in books)


@pytest.mark.asyncio
async def test_filter_by_pub_year_returns_empty_for_unknown(filter_client: httpx.AsyncClient) -> None:
    response = await filter_client.get('/api/v1/books', params={'pub_year': 1111, 'limit': 100})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_search_by_title(filter_client: httpx.AsyncClient) -> None:
    response = await filter_client.get('/api/v1/books', params={'search': 'мир', 'limit': 100})
    assert response.status_code == 200
    books = response.json()
    assert len(books) == 1
    assert books[0]['title'] == 'Война и мир'


@pytest.mark.asyncio
async def test_search_is_case_insensitive(filter_client: httpx.AsyncClient) -> None:
    response = await filter_client.get('/api/v1/books', params={'search': 'МИР', 'limit': 100})
    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_search_returns_empty_for_no_match(filter_client: httpx.AsyncClient) -> None:
    response = await filter_client.get('/api/v1/books', params={'search': 'xyznotexist', 'limit': 100})
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_pagination_limit(filter_client: httpx.AsyncClient) -> None:
    response = await filter_client.get('/api/v1/books', params={'limit': 2})
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_pagination_offset(filter_client: httpx.AsyncClient) -> None:
    response = await filter_client.get('/api/v1/books', params={'limit': 100, 'offset': 3})
    assert response.status_code == 200
    assert len(response.json()) == 2


@pytest.mark.asyncio
async def test_pagination_limit_and_offset_combined(filter_client: httpx.AsyncClient) -> None:
    response = await filter_client.get('/api/v1/books', params={'limit': 2, 'offset': 2})
    assert response.status_code == 200
    assert len(response.json()) == 2
