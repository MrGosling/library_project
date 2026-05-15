# tests/test_categories.py
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_category(async_client: AsyncClient):
    response = await async_client.post('/api/v1/categories/', json={'name': 'Роман'})
    assert response.status_code == 201
    assert response.json()['name'] == 'Роман'


@pytest.mark.asyncio
async def test_create_category_with_description(async_client: AsyncClient):
    response = await async_client.post(
        '/api/v1/categories/', json={'name': 'Рассказ', 'description': 'Короткое прозаическое произведение'}
    )
    assert response.status_code == 201
    assert response.json()['name'] == 'Рассказ'
    assert response.json()['description'] == 'Короткое прозаическое произведение'


@pytest.mark.asyncio
async def test_get_categories(async_client: AsyncClient):
    response = await async_client.get('/api/v1/categories/')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_category_by_id(async_client: AsyncClient):
    create = await async_client.post('/api/v1/categories/', json={'name': 'Пьеса'})
    category_id = create.json()['id']
    response = await async_client.get(f'/api/v1/categories/{category_id}')
    assert response.status_code == 200
    assert response.json()['id'] == category_id


@pytest.mark.asyncio
async def test_get_category_not_found(async_client: AsyncClient):
    response = await async_client.get('/api/v1/categories/99999')
    assert response.status_code == 404
    assert response.json()['detail'] == 'Category not found'


@pytest.mark.asyncio
async def test_update_category_is_not_supported(async_client: AsyncClient):
    create = await async_client.post('/api/v1/categories/', json={'name': 'Поэма'})
    category_id = create.json()['id']
    response = await async_client.patch(
        f'/api/v1/categories/{category_id}',
        json={'name': 'Поэма обновлённая', 'description': 'Лирическое произведение'},
    )
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_update_category_not_supported_for_missing_category(async_client: AsyncClient):
    response = await async_client.patch('/api/v1/categories/99999', json={'name': 'Не существует'})
    assert response.status_code == 405


@pytest.mark.asyncio
async def test_delete_category(async_client: AsyncClient):
    create = await async_client.post('/api/v1/categories/', json={'name': 'Удаляемая'})
    category_id = create.json()['id']
    response = await async_client.delete(f'/api/v1/categories/{category_id}')
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_category_not_found(async_client: AsyncClient):
    response = await async_client.delete('/api/v1/categories/99999')
    assert response.status_code == 404
