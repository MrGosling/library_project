from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models.genre import Genre
from app.schemas.genre import GenreCreate, GenreRead

router = APIRouter()


async def get_genre_or_404(
    genre_id: int,
    session: AsyncSession,
) -> Genre:
    """Получить жанр по ID или вернуть 404."""
    genre = await session.get(Genre, genre_id)
    if genre is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Genre not found',
        )
    return genre


@router.get(
    '/',
    response_model=list[GenreRead],
    summary='Список жанров',
    description='Возвращает все жанры из базы данных.',
)
async def get_genres(
    session: AsyncSession = Depends(get_async_session),
) -> list[GenreRead]:
    """Получить список всех жанров."""
    result = await session.execute(select(Genre))
    return result.scalars().all()


@router.get(
    '/{genre_id}',
    response_model=GenreRead,
    summary='Получить жанр',
    description='Возвращает жанр по его ID.',
)
async def get_genre(
    genre_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> GenreRead:
    """Получить жанр по ID."""
    return await get_genre_or_404(genre_id, session)


@router.post(
    '/',
    response_model=GenreRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создать жанр',
    description='Создаёт новый жанр. Имя должно быть уникальным.',
)
async def create_genre(
    data: GenreCreate,
    session: AsyncSession = Depends(get_async_session),
) -> GenreRead:
    """Создать новый жанр с проверкой уникальности имени."""
    existing = await session.execute(select(Genre).where(Genre.name == data.name))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Genre with this name already exists',
        )
    genre = Genre(**data.model_dump())
    session.add(genre)
    await session.commit()
    await session.refresh(genre)
    return genre


@router.delete(
    '/{genre_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удалить жанр',
    description='Удаляет жанр по ID.',
)
async def delete_genre(
    genre_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Удалить жанр по ID."""
    genre = await get_genre_or_404(genre_id, session)
    await session.delete(genre)
    await session.commit()
