from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_async_session
from backend.models.favorite import Favorite
from backend.schemas.favorite import FavoriteCreate, FavoriteRead

router = APIRouter()


async def get_favorite_or_404(favorite_id: int, session: AsyncSession) -> Favorite:
    favorite = await session.get(Favorite, favorite_id)
    if favorite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Favorite not found',
        )
    return favorite


@router.get('/', response_model=list[FavoriteRead], summary='Список избранного')
async def get_favorites(session: AsyncSession = Depends(get_async_session)) -> list[FavoriteRead]:
    result = await session.execute(select(Favorite))
    return result.scalars().all()


@router.get('/{favorite_id}', response_model=FavoriteRead, summary='Получить избранное')
async def get_favorite(favorite_id: int, session: AsyncSession = Depends(get_async_session)) -> FavoriteRead:
    return await get_favorite_or_404(favorite_id, session)


@router.post('/', response_model=FavoriteRead, status_code=status.HTTP_201_CREATED, summary='Добавить в избранное')
async def create_favorite(data: FavoriteCreate, session: AsyncSession = Depends(get_async_session)) -> FavoriteRead:
    favorite = Favorite(**data.model_dump())
    session.add(favorite)
    await session.commit()
    await session.refresh(favorite)
    return favorite


@router.delete('/{favorite_id}', status_code=status.HTTP_204_NO_CONTENT, summary='Удалить из избранного')
async def delete_favorite(favorite_id: int, session: AsyncSession = Depends(get_async_session)) -> None:
    favorite = await get_favorite_or_404(favorite_id, session)
    await session.delete(favorite)
    await session.commit()
