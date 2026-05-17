import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.v1.endpoints.favorites import router as favorites_router
from backend.core.db import get_async_session
from backend.models.favorite import Favorite


class FakeScalarResult:
    def __init__(self, items: list[Favorite]) -> None:
        self.items = items

    def all(self) -> list[Favorite]:
        return self.items


class FakeResult:
    def __init__(self, items: list[Favorite]) -> None:
        self.items = items

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self.items)


class FakeFavoriteSession:
    def __init__(self) -> None:
        self.favorites: list[Favorite] = [
            self._build_favorite(favorite_id=1, user_id=1, book_id=1, is_read=False)
        ]
        self._next_id = 2

    async def execute(self, statement) -> FakeResult:
        return FakeResult(list(self.favorites))

    async def get(self, model: type, item_id: int) -> Favorite | None:
        return next((f for f in self.favorites if f.id == item_id), None)

    def add(self, favorite: Favorite) -> None:
        favorite.id = self._next_id
        self._next_id += 1
        self.favorites.append(favorite)

    async def commit(self) -> None:
        return None

    async def refresh(self, favorite: Favorite) -> None:
        return None

    async def delete(self, favorite: Favorite) -> None:
        self.favorites.remove(favorite)

    @staticmethod
    def _build_favorite(favorite_id: int, user_id: int, book_id: int, is_read: bool = False) -> Favorite:
        favorite = Favorite(user_id=user_id, book_id=book_id, is_read=is_read)
        favorite.id = favorite_id
        return favorite


@pytest.fixture
def fake_session() -> FakeFavoriteSession:
    return FakeFavoriteSession()


@pytest.fixture
def client(fake_session: FakeFavoriteSession) -> TestClient:
    app = FastAPI()
    app.include_router(favorites_router, prefix='/api/v1/favorites')

    async def override_get_async_session():
        yield fake_session

    app.dependency_overrides[get_async_session] = override_get_async_session
    return TestClient(app)


def test_get_favorites_returns_list(client: TestClient) -> None:
    response = client.get('/api/v1/favorites/')

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['is_read'] is False


def test_get_favorite_by_id(client: TestClient) -> None:
    response = client.get('/api/v1/favorites/1')

    assert response.status_code == 200
    assert response.json()['id'] == 1
    assert response.json()['user_id'] == 1
    assert response.json()['book_id'] == 1


def test_get_favorite_returns_404_for_missing_favorite(client: TestClient) -> None:
    response = client.get('/api/v1/favorites/999')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Favorite not found'}


def test_create_favorite(client: TestClient, fake_session: FakeFavoriteSession) -> None:
    response = client.post(
        '/api/v1/favorites/',
        json={'user_id': 2, 'book_id': 3, 'is_read': False},
    )

    assert response.status_code == 201
    assert response.json()['user_id'] == 2
    assert response.json()['book_id'] == 3
    assert len(fake_session.favorites) == 2


def test_create_favorite_with_is_read(client: TestClient, fake_session: FakeFavoriteSession) -> None:
    response = client.post(
        '/api/v1/favorites/',
        json={'user_id': 1, 'book_id': 2, 'is_read': True},
    )

    assert response.status_code == 201
    assert response.json()['is_read'] is True


def test_delete_favorite(client: TestClient, fake_session: FakeFavoriteSession) -> None:
    response = client.delete('/api/v1/favorites/1')

    assert response.status_code == 204
    assert len(fake_session.favorites) == 0


def test_delete_favorite_returns_404_for_missing_favorite(client: TestClient) -> None:
    response = client.delete('/api/v1/favorites/999')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Favorite not found'}
