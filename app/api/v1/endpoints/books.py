from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models.author import Author
from app.models.book import Book
from app.schemas.book import BookCreate, BookRead

router = APIRouter()


def book_or_404(book: Book | None) -> Book:
    """Возвращает книгу или ошибку 404."""
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Книга не найдена',
        )
    return book


async def check_author_exists(author_id: int, session: AsyncSession) -> Author:
    """Проверяет существует ли автор, иначе ошибка 404"""
    author = await session.get(Author, author_id)
    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Автор не найден',
        )
    return author


@router.post(
    '',
    response_model=BookRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создать книгу',
)
async def create_book(
    book_data: BookCreate,
    session: AsyncSession = Depends(get_async_session),
) -> Book:
    """Создаёт книгу"""
    await check_author_exists(book_data.author_id, session)

    book = Book(**book_data.model_dump())
    session.add(book)
    await session.commit()
    await session.refresh(book)
    return book


@router.get(
    '',
    response_model=list[BookRead],
    summary='Список книг',
)
async def get_books(
    session: AsyncSession = Depends(get_async_session),
) -> list[Book]:
    """Возвращает список книг"""
    statement = select(Book)
    result = await session.execute(statement)
    return list(result.scalars().all())


@router.get(
    '/{book_id}',
    response_model=BookRead,
    summary='Получить книгу по ID',
)
async def get_book(
    book_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> Book:
    """Возвращает книгу по ID"""
    book = await session.get(Book, book_id)
    return book_or_404(book)


@router.delete(
    '/{book_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удалить книгу',
)
async def delete_book(
    book_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Удаляет книгу по ID"""
    book = await session.get(Book, book_id)
    book = book_or_404(book)

    await session.delete(book)
    await session.commit()
    return None