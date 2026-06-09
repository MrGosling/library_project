import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_category(async_client: AsyncClient) -> None:
    response = await async_client.post(
        '/api/v1/categories',
        json={'name': 'Научная фантастика', 'description': 'О будущем и технологиях'},
    )

    assert response.status_code == 201
    assert response.json()['name'] == 'Научная фантастика'


@pytest.mark.asyncio
async def test_get_categories(async_client: AsyncClient) -> None:
    await async_client.post('/api/v1/categories', json={'name': 'Cat 1'})
    await async_client.post('/api/v1/categories', json={'name': 'Cat 2'})

    response = await async_client.get('/api/v1/categories')

    assert response.status_code == 200
    names = [c['name'] for c in response.json()]
    assert 'Cat 1' in names
    assert 'Cat 2' in names


@pytest.mark.asyncio
async def test_delete_category(async_client: AsyncClient) -> None:
    create = await async_client.post('/api/v1/categories', json={'name': 'To Delete'})
    cat_id = create.json()['id']

    response = await async_client.delete(f'/api/v1/categories/{cat_id}')
    assert response.status_code == 204
