from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models.genre import Genre
from app.schemas.genre import GenreCreate, GenreRead, GenreUpdate

router = APIRouter()


@router.get("/", response_model=list[GenreRead])
async def get_genres(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(select(Genre))
    return result.scalars().all()


@router.get("/{genre_id}", response_model=GenreRead)
async def get_genre(genre_id: int, session: AsyncSession = Depends(get_async_session)):
    genre = await session.get(Genre, genre_id)
    if genre is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    return genre


@router.post("/", response_model=GenreRead, status_code=status.HTTP_201_CREATED)
async def create_genre(data: GenreCreate, session: AsyncSession = Depends(get_async_session)):
    genre = Genre(**data.model_dump())
    session.add(genre)
    await session.commit()
    await session.refresh(genre)
    return genre


@router.patch("/{genre_id}", response_model=GenreRead)
async def update_genre(genre_id: int, data: GenreUpdate, session: AsyncSession = Depends(get_async_session)):
    genre = await session.get(Genre, genre_id)
    if genre is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(genre, field, value)
    await session.commit()
    await session.refresh(genre)
    return genre


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(genre_id: int, session: AsyncSession = Depends(get_async_session)):
    genre = await session.get(Genre, genre_id)
    if genre is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    await session.delete(genre)
    await session.commit()
