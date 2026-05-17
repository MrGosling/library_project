import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_book(async_client: AsyncClient) -> None:
    response = await async_client.post(
        '/api/v1/books',
        json={
            'title': 'Война и мир',
            'pub_year': 1869,
            'author_id': 1,
            'description': 'Роман-эпопея',
        },
    )

    assert response.status_code == 201
    assert response.json()['title'] == 'Война и мир'
    assert response.json()['author_id'] == 1


@pytest.mark.asyncio
async def test_create_book_returns_404_for_missing_author(
    async_client: AsyncClient,
) -> None:
    response = await async_client.post(
        '/api/v1/books',
        json={
            'title': 'Неизданная книга',
            'pub_year': 2024,
            'author_id': 999,
        },
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'Автор не найден'}


@pytest.mark.asyncio
async def test_get_books(async_client: AsyncClient) -> None:
    await async_client.post(
        '/api/v1/books',
        json={'title': 'Книга 1', 'pub_year': 2001, 'author_id': 1},
    )
    await async_client.post(
        '/api/v1/books',
        json={'title': 'Книга 2', 'pub_year': 2002, 'author_id': 1},
    )

    response = await async_client.get('/api/v1/books')

    assert response.status_code == 200
    assert [book['title'] for book in response.json()] == [
        'Книга 1',
        'Книга 2',
    ]


@pytest.mark.asyncio
async def test_get_book_by_id(async_client: AsyncClient) -> None:
    create = await async_client.post(
        '/api/v1/books',
        json={'title': 'Идиот', 'pub_year': 1869, 'author_id': 1},
    )
    book_id = create.json()['id']

    response = await async_client.get(f'/api/v1/books/{book_id}')

    assert response.status_code == 200
    assert response.json()['id'] == book_id
    assert response.json()['title'] == 'Идиот'


@pytest.mark.asyncio
async def test_get_book_returns_404_for_missing_book(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get('/api/v1/books/999')

    assert response.status_code == 404
    assert response.json() == {'detail': 'Книга не найдена'}


@pytest.mark.asyncio
async def test_delete_book(async_client: AsyncClient) -> None:
    create = await async_client.post(
        '/api/v1/books',
        json={'title': 'Удаляемая книга', 'pub_year': 2000, 'author_id': 1},
    )
    book_id = create.json()['id']

    response = await async_client.delete(f'/api/v1/books/{book_id}')
    get_response = await async_client.get(f'/api/v1/books/{book_id}')

    assert response.status_code == 204
    assert get_response.status_code == 404
