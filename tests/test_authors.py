import pytest
from httpx import AsyncClient
from datetime import date
from pydantic import ValidationError

from backend.schemas.author import AuthorCreate


@pytest.mark.asyncio
async def test_get_authors_returns_authors(async_client: AsyncClient) -> None:
    response = await async_client.get('/api/v1/authors')

    assert response.status_code == 200
    # Initial fake author with id 1 is created in FakeLibrarySession
    assert response.json()[0]['id'] == 1


@pytest.mark.asyncio
async def test_get_author_returns_author(async_client: AsyncClient) -> None:
    response = await async_client.get('/api/v1/authors/1')

    assert response.status_code == 200
    assert response.json()['full_name'] == 'Тестовый автор'


@pytest.mark.asyncio
async def test_get_author_returns_404_for_missing_author(async_client: AsyncClient) -> None:
    response = await async_client.get('/api/v1/authors/404')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Автор не найден'}


@pytest.mark.asyncio
async def test_create_author(async_client: AsyncClient) -> None:
    response = await async_client.post(
        '/api/v1/authors',
        json={
            'full_name': '  Антон Павлович Чехов  ',
            'birth_year': 1860,
            'bio': 'Писатель и драматург',
        },
    )

    assert response.status_code == 201
    assert response.json()['full_name'] == 'Антон Павлович Чехов'


@pytest.mark.asyncio
async def test_update_author_accepts_partial_payload(async_client: AsyncClient) -> None:
    response = await async_client.patch(
        '/api/v1/authors/1', json={'bio': 'Обновленная биография'}
    )

    assert response.status_code == 200
    assert response.json()['bio'] == 'Обновленная биография'


@pytest.mark.asyncio
async def test_delete_author(async_client: AsyncClient) -> None:
    # Create an author to delete (id 1 exists but might be linked)
    create_resp = await async_client.post(
        '/api/v1/authors',
        json={'full_name': 'Delete Me', 'birth_year': 2000}
    )
    author_id = create_resp.json()['id']
    
    response = await async_client.delete(f'/api/v1/authors/{author_id}')
    assert response.status_code == 204
    
    get_response = await async_client.get(f'/api/v1/authors/{author_id}')
    assert get_response.status_code == 404


def test_author_create_strips_full_name() -> None:
    author = AuthorCreate(full_name='  Иван Сергеевич Тургенев  ')
    assert author.full_name == 'Иван Сергеевич Тургенев'


def test_author_create_rejects_blank_full_name() -> None:
    with pytest.raises(ValidationError):
        AuthorCreate(full_name='   ')


def test_author_create_rejects_future_birth_year() -> None:
    with pytest.raises(ValidationError):
        AuthorCreate(full_name='Автор', birth_year=date.today().year + 1)
