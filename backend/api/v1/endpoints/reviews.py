from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_async_session
from backend.models.review import Review
from backend.schemas.review import ReviewCreate, ReviewRead

router = APIRouter()


async def get_review_or_404(review_id: int, session: AsyncSession) -> Review:
    review = await session.get(Review, review_id)
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Review not found',
        )
    return review


@router.get('/', response_model=list[ReviewRead], summary='Список отзывов')
async def get_reviews(session: AsyncSession = Depends(get_async_session)) -> list[ReviewRead]:
    result = await session.execute(select(Review))
    return result.scalars().all()


@router.get('/{review_id}', response_model=ReviewRead, summary='Получить отзыв')
async def get_review(review_id: int, session: AsyncSession = Depends(get_async_session)) -> ReviewRead:
    return await get_review_or_404(review_id, session)


@router.post('/', response_model=ReviewRead, status_code=status.HTTP_201_CREATED, summary='Создать отзыв')
async def create_review(data: ReviewCreate, session: AsyncSession = Depends(get_async_session)) -> ReviewRead:
    review = Review(**data.model_dump())
    session.add(review)
    await session.commit()
    await session.refresh(review)
    return review


@router.delete('/{review_id}', status_code=status.HTTP_204_NO_CONTENT, summary='Удалить отзыв')
async def delete_review(review_id: int, session: AsyncSession = Depends(get_async_session)) -> None:
    review = await get_review_or_404(review_id, session)
    await session.delete(review)
    await session.commit()
