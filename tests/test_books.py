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
async def test_replace_book(async_client: AsyncClient) -> None:
    create = await async_client.post(
        '/api/v1/books',
        json={
            'title': 'Черновик',
            'pub_year': 2000,
            'author_id': 1,
            'description': 'Старое описание',
        },
    )
    book_id = create.json()['id']

    response = await async_client.put(
        f'/api/v1/books/{book_id}',
        json={'title': 'Анна Каренина', 'pub_year': 1877, 'author_id': 1},
    )

    assert response.status_code == 200
    assert response.json()['title'] == 'Анна Каренина'
    assert response.json()['pub_year'] == 1877
    assert response.json()['description'] is None


@pytest.mark.asyncio
async def test_replace_book_requires_all_fields(
    async_client: AsyncClient,
) -> None:
    create = await async_client.post(
        '/api/v1/books',
        json={'title': 'Книга', 'pub_year': 2000, 'author_id': 1},
    )
    book_id = create.json()['id']

    response = await async_client.put(
        f'/api/v1/books/{book_id}', json={'title': 'Только название'}
    )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_replace_book_returns_404_for_missing_book(
    async_client: AsyncClient,
) -> None:
    response = await async_client.put(
        '/api/v1/books/999',
        json={'title': 'Нет такой', 'pub_year': 2000, 'author_id': 1},
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'Книга не найдена'}


@pytest.mark.asyncio
async def test_update_book_accepts_partial_payload(
    async_client: AsyncClient,
) -> None:
    create = await async_client.post(
        '/api/v1/books',
        json={'title': 'Бесы', 'pub_year': 1800, 'author_id': 1},
    )
    book_id = create.json()['id']

    response = await async_client.patch(
        f'/api/v1/books/{book_id}', json={'pub_year': 1872}
    )

    assert response.status_code == 200
    assert response.json()['pub_year'] == 1872
    assert response.json()['title'] == 'Бесы'


@pytest.mark.asyncio
async def test_update_book_returns_404_for_missing_author(
    async_client: AsyncClient,
) -> None:
    create = await async_client.post(
        '/api/v1/books',
        json={'title': 'Книга', 'pub_year': 2000, 'author_id': 1},
    )
    book_id = create.json()['id']

    response = await async_client.patch(
        f'/api/v1/books/{book_id}', json={'author_id': 999}
    )

    assert response.status_code == 404
    assert response.json() == {'detail': 'Автор не найден'}


@pytest.mark.asyncio
async def test_update_book_returns_404_for_missing_book(
    async_client: AsyncClient,
) -> None:
    response = await async_client.patch(
        '/api/v1/books/999', json={'pub_year': 2000}
    )

    assert response.status_code == 404


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
