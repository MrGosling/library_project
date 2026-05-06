import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_genre(async_client: AsyncClient):
    response = await async_client.post('/api/v1/genres/', json={'name': 'Фантастика'})
    assert response.status_code == 201
    assert response.json()['name'] == 'Фантастика'


@pytest.mark.asyncio
async def test_get_genres(async_client: AsyncClient):
    response = await async_client.get('/api/v1/genres/')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_genre_not_found(async_client: AsyncClient):
    response = await async_client.get('/api/v1/genres/99999')
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_genre(async_client: AsyncClient):
    create = await async_client.post('/api/v1/genres/', json={'name': 'Детектив'})
    genre_id = create.json()['id']
    response = await async_client.patch(f'/api/v1/genres/{genre_id}', json={'name': 'Детектив обновлён'})
    assert response.status_code == 200
    assert response.json()['name'] == 'Детектив обновлён'


@pytest.mark.asyncio
async def test_delete_genre(async_client: AsyncClient):
    create = await async_client.post('/api/v1/genres/', json={'name': 'Удаляемый'})
    genre_id = create.json()['id']
    response = await async_client.delete(f'/api/v1/genres/{genre_id}')
    assert response.status_code == 204
