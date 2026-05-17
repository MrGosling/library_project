import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.api.v1.endpoints.reviews import router as reviews_router
from backend.core.db import get_async_session
from backend.models.review import Review


class FakeScalarResult:
    def __init__(self, items: list[Review]) -> None:
        self.items = items

    def all(self) -> list[Review]:
        return self.items


class FakeResult:
    def __init__(self, items: list[Review]) -> None:
        self.items = items

    def scalars(self) -> FakeScalarResult:
        return FakeScalarResult(self.items)


class FakeReviewSession:
    def __init__(self) -> None:
        self.reviews: list[Review] = [
            self._build_review(review_id=1, rating=5, book_id=1, user_id=1, text='Отличная книга')
        ]
        self._next_id = 2

    async def execute(self, statement) -> FakeResult:
        return FakeResult(list(self.reviews))

    async def get(self, model: type, item_id: int) -> Review | None:
        return next((r for r in self.reviews if r.id == item_id), None)

    def add(self, review: Review) -> None:
        review.id = self._next_id
        self._next_id += 1
        self.reviews.append(review)

    async def commit(self) -> None:
        return None

    async def refresh(self, review: Review) -> None:
        return None

    async def delete(self, review: Review) -> None:
        self.reviews.remove(review)

    @staticmethod
    def _build_review(review_id: int, rating: int, book_id: int, user_id: int, text: str | None = None) -> Review:
        review = Review(rating=rating, text=text, book_id=book_id, user_id=user_id)
        review.id = review_id
        return review


@pytest.fixture
def fake_session() -> FakeReviewSession:
    return FakeReviewSession()


@pytest.fixture
def client(fake_session: FakeReviewSession) -> TestClient:
    app = FastAPI()
    app.include_router(reviews_router, prefix='/api/v1/reviews')

    async def override_get_async_session():
        yield fake_session

    app.dependency_overrides[get_async_session] = override_get_async_session
    return TestClient(app)


def test_get_reviews_returns_list(client: TestClient) -> None:
    response = client.get('/api/v1/reviews/')

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['rating'] == 5


def test_get_review_by_id(client: TestClient) -> None:
    response = client.get('/api/v1/reviews/1')

    assert response.status_code == 200
    assert response.json()['id'] == 1
    assert response.json()['text'] == 'Отличная книга'


def test_get_review_returns_404_for_missing_review(client: TestClient) -> None:
    response = client.get('/api/v1/reviews/999')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Review not found'}


def test_create_review(client: TestClient, fake_session: FakeReviewSession) -> None:
    response = client.post(
        '/api/v1/reviews/',
        json={'rating': 4, 'text': 'Хорошая книга', 'book_id': 2, 'user_id': 1},
    )

    assert response.status_code == 201
    assert response.json()['rating'] == 4
    assert response.json()['text'] == 'Хорошая книга'
    assert len(fake_session.reviews) == 2


def test_create_review_without_text(client: TestClient, fake_session: FakeReviewSession) -> None:
    response = client.post(
        '/api/v1/reviews/',
        json={'rating': 3, 'book_id': 1, 'user_id': 2},
    )

    assert response.status_code == 201
    assert response.json()['text'] is None


def test_delete_review(client: TestClient, fake_session: FakeReviewSession) -> None:
    response = client.delete('/api/v1/reviews/1')

    assert response.status_code == 204
    assert len(fake_session.reviews) == 0


def test_delete_review_returns_404_for_missing_review(client: TestClient) -> None:
    response = client.delete('/api/v1/reviews/999')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Review not found'}
