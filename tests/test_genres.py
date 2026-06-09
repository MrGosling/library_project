import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_genre(async_client: AsyncClient) -> None:
    response = await async_client.post(
        '/api/v1/genres',
        json={'name': 'Киберпанк'},
    )

    assert response.status_code == 201
    assert response.json()['name'] == 'Киберпанк'


@pytest.mark.asyncio
async def test_get_genres(async_client: AsyncClient) -> None:
    await async_client.post('/api/v1/genres', json={'name': 'Genre 1'})

    response = await async_client.get('/api/v1/genres')

    assert response.status_code == 200
    names = [g['name'] for g in response.json()]
    assert 'Genre 1' in names


@pytest.mark.asyncio
async def test_delete_genre(async_client: AsyncClient) -> None:
    create = await async_client.post('/api/v1/genres', json={'name': 'To Delete'})
    genre_id = create.json()['id']

    response = await async_client.delete(f'/api/v1/genres/{genre_id}')
    assert response.status_code == 204
