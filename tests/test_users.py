from datetime import datetime, timezone

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.v1.endpoints.users import router as users_router
from backend.core.db import get_async_session
from backend.core.security import hash_password
from backend.models.user import User


class FakeScalarResult:
    def __init__(self, items: list[User]) -> None:
        self.items = items

    def all(self) -> list[User]:
        return self.items


class FakeResult:
    def __init__(self, items: list[User]) -> None:
        self.items = items

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self.items)

    def scalar_one_or_none(self) -> User | None:
        if not self.items:
            return None
        return self.items[0]


class FakeUserSession:
    def __init__(self) -> None:
        self.users: list[User] = [
            self._build_user(1, 'existinguser', 'existing@example.com', hash_password('secret123'))
        ]
        self._next_id = 2

    async def execute(self, statement) -> FakeResult:
        items = list(self.users)
        if statement.whereclause is not None:
            params = statement.compile().params
            for key, value in params.items():
                if 'username' in key:
                    items = [u for u in items if u.username == value]
                elif 'email' in key:
                    items = [u for u in items if u.email == value]
        return FakeResult(items)

    async def get(self, model: type, item_id: int) -> User | None:
        return next((u for u in self.users if u.id == item_id), None)

    def add(self, user: User) -> None:
        user.id = self._next_id
        user.created_at = datetime.now(timezone.utc)
        self._next_id += 1
        self.users.append(user)

    async def commit(self) -> None:
        return None

    async def refresh(self, user: User) -> None:
        return None

    @staticmethod
    def _build_user(user_id: int, username: str, email: str, hashed_password: str) -> User:
        user = User(
            username=username,
            email=email,
            password=hashed_password,
            is_active=True,
            is_superuser=False,
            role='reader',
        )
        user.id = user_id
        user.created_at = datetime.now(timezone.utc)
        return user


@pytest.fixture
def fake_session() -> FakeUserSession:
    return FakeUserSession()


@pytest.fixture
def client(fake_session: FakeUserSession) -> TestClient:
    app = FastAPI()
    app.include_router(users_router, prefix='/api/v1/users')

    async def override_get_async_session():
        yield fake_session

    app.dependency_overrides[get_async_session] = override_get_async_session
    return TestClient(app)


def test_register_creates_user(client: TestClient, fake_session: FakeUserSession) -> None:
    response = client.post(
        '/api/v1/users/register',
        json={'username': 'newuser', 'email': 'new@example.com', 'password': 'password123'},
    )

    assert response.status_code == 201
    assert response.json()['username'] == 'newuser'
    assert response.json()['role'] == 'reader'
    assert len(fake_session.users) == 2


def test_register_fails_on_duplicate_username(client: TestClient) -> None:
    response = client.post(
        '/api/v1/users/register',
        json={'username': 'existinguser', 'email': 'other@example.com', 'password': 'password123'},
    )

    assert response.status_code == 400
    assert response.json() == {'detail': 'Username already registered'}


def test_register_fails_on_duplicate_email(client: TestClient) -> None:
    response = client.post(
        '/api/v1/users/register',
        json={'username': 'newuser', 'email': 'existing@example.com', 'password': 'password123'},
    )

    assert response.status_code == 400
    assert response.json() == {'detail': 'Email already registered'}


def test_login_returns_token(client: TestClient) -> None:
    response = client.post(
        '/api/v1/users/login',
        json={'username': 'existinguser', 'password': 'secret123'},
    )

    assert response.status_code == 200
    assert response.json()['access_token'] == 'token_1'
    assert response.json()['token_type'] == 'bearer'


def test_login_fails_with_wrong_password(client: TestClient) -> None:
    response = client.post(
        '/api/v1/users/login',
        json={'username': 'existinguser', 'password': 'wrongpassword'},
    )

    assert response.status_code == 401


def test_login_fails_with_unknown_username(client: TestClient) -> None:
    response = client.post(
        '/api/v1/users/login',
        json={'username': 'nobody', 'password': 'secret123'},
    )

    assert response.status_code == 401


def test_change_password_success(client: TestClient) -> None:
    response = client.post(
        '/api/v1/users/change-password',
        json={'username': 'existinguser', 'old_password': 'secret123', 'new_password': 'newsecret'},
    )

    assert response.status_code == 200

    login = client.post(
        '/api/v1/users/login',
        json={'username': 'existinguser', 'password': 'newsecret'},
    )
    assert login.status_code == 200


def test_change_password_fails_with_wrong_old_password(client: TestClient) -> None:
    response = client.post(
        '/api/v1/users/change-password',
        json={'username': 'existinguser', 'old_password': 'wrongpass', 'new_password': 'newsecret'},
    )

    assert response.status_code == 401


def test_refresh_token_returns_token(client: TestClient) -> None:
    response = client.post('/api/v1/users/refresh-token', json={'token': 'token_1'})

    assert response.status_code == 200
    assert response.json()['access_token'] == 'token_1'


def test_refresh_token_fails_with_invalid_token(client: TestClient) -> None:
    response = client.post('/api/v1/users/refresh-token', json={'token': 'invalid_token'})

    assert response.status_code == 401
