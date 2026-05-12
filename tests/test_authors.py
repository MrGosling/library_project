from datetime import date, datetime, timezone

import pytest
from app.api.v1.api import api_router
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.db import get_async_session
from app.models.author import Author
from app.schemas.author import AuthorCreate, AuthorUpdate


class FakeScalarResult:
    def __init__(self, items: list[Author]) -> None:
        self.items = items

    def all(self) -> list[Author]:
        return self.items


class FakeResult:
    def __init__(self, items: list[Author]) -> None:
        self.items = items

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self.items)


class FakeAuthorSession:
    def __init__(self) -> None:
        self.authors = [
            self._build_author(
                author_id=1,
                full_name='Лев Николаевич Толстой',
                birth_year=1828,
                bio='Автор романа Война и мир',
            ),
            self._build_author(
                author_id=2,
                full_name='Федор Михайлович Достоевский',
                birth_year=1821,
                bio=None,
            ),
        ]
        self.commits = 0

    async def execute(self, statement) -> FakeResult:
        return FakeResult(self.authors)

    async def get(self, model, author_id: int) -> Author | None:
        return next((author for author in self.authors if author.id == author_id), None)

    def add(self, author: Author) -> None:
        author.id = max(existing.id for existing in self.authors) + 1
        author.created_at = datetime.now(timezone.utc)
        author.updated_at = author.created_at
        self.authors.append(author)

    async def commit(self) -> None:
        self.commits += 1

    async def refresh(self, author: Author) -> None:
        author.updated_at = datetime.now(timezone.utc)

    async def delete(self, author: Author) -> None:
        self.authors.remove(author)

    @staticmethod
    def _build_author(
        author_id: int,
        full_name: str,
        birth_year: int | None,
        bio: str | None,
    ) -> Author:
        now = datetime.now(timezone.utc)
        author = Author(
            full_name=full_name,
            birth_year=birth_year,
            bio=bio,
        )
        author.id = author_id
        author.created_at = now
        author.updated_at = now
        return author


@pytest.fixture
def fake_session() -> FakeAuthorSession:
    return FakeAuthorSession()


@pytest.fixture
def client(fake_session: FakeAuthorSession) -> TestClient:
    app = FastAPI()
    app.include_router(api_router, prefix='/api/v1')

    async def override_get_async_session():
        yield fake_session

    app.dependency_overrides[get_async_session] = override_get_async_session
    return TestClient(app)


def test_get_authors_returns_authors(client: TestClient) -> None:
    response = client.get('/api/v1/authors')

    assert response.status_code == 200
    assert [author['id'] for author in response.json()] == [1, 2]


def test_get_author_returns_author(client: TestClient) -> None:
    response = client.get('/api/v1/authors/1')

    assert response.status_code == 200
    assert response.json()['full_name'] == 'Лев Николаевич Толстой'


def test_get_author_returns_404_for_missing_author(client: TestClient) -> None:
    response = client.get('/api/v1/authors/404')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Автор не найден'}


def test_create_author(client: TestClient, fake_session: FakeAuthorSession) -> None:
    response = client.post(
        '/api/v1/authors',
        json={
            'full_name': '  Антон Павлович Чехов  ',
            'birth_year': 1860,
            'bio': 'Писатель и драматург',
        },
    )

    assert response.status_code == 201
    assert response.json()['full_name'] == 'Антон Павлович Чехов'
    assert fake_session.commits == 1
    assert fake_session.authors[-1].full_name == 'Антон Павлович Чехов'


def test_update_author_accepts_partial_payload(
    client: TestClient,
    fake_session: FakeAuthorSession,
) -> None:
    response = client.patch('/api/v1/authors/1', json={'bio': 'Обновленная биография'})

    assert response.status_code == 200
    assert response.json()['bio'] == 'Обновленная биография'
    assert fake_session.authors[0].full_name == 'Лев Николаевич Толстой'
    assert fake_session.commits == 1


def test_update_author_returns_404_for_missing_author(client: TestClient) -> None:
    response = client.patch('/api/v1/authors/404', json={'bio': 'Не важно'})

    assert response.status_code == 404
    assert response.json() == {'detail': 'Автор не найден'}


def test_delete_author(client: TestClient, fake_session: FakeAuthorSession) -> None:
    response = client.delete('/api/v1/authors/1')

    assert response.status_code == 204
    assert [author.id for author in fake_session.authors] == [2]
    assert fake_session.commits == 1


def test_delete_author_returns_404_for_missing_author(client: TestClient) -> None:
    response = client.delete('/api/v1/authors/404')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Автор не найден'}


def test_author_create_strips_full_name() -> None:
    author = AuthorCreate(full_name='  Иван Сергеевич Тургенев  ')

    assert author.full_name == 'Иван Сергеевич Тургенев'


def test_author_create_rejects_blank_full_name() -> None:
    with pytest.raises(ValidationError):
        AuthorCreate(full_name='   ')


def test_author_create_rejects_future_birth_year() -> None:
    with pytest.raises(ValidationError):
        AuthorCreate(full_name='Автор', birth_year=date.today().year + 1)


def test_author_update_allows_partial_payload() -> None:
    update = AuthorUpdate(bio='Только биография')

    assert update.model_dump(exclude_unset=True) == {'bio': 'Только биография'}
