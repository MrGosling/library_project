from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryRead

router = APIRouter()


async def get_category_or_404(
    category_id: int,
    session: AsyncSession,
) -> Category:
    """Получить категорию по ID или вернуть 404."""
    category = await session.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Category not found',
        )
    return category


@router.get(
    '/',
    response_model=list[CategoryRead],
    summary='Список категорий',
    description='Возвращает все категории из базы данных.',
)
async def get_categories(
    session: AsyncSession = Depends(get_async_session),
) -> list[CategoryRead]:
    """Получить список всех категорий."""
    result = await session.execute(select(Category))
    return result.scalars().all()


@router.get(
    '/{category_id}',
    response_model=CategoryRead,
    summary='Получить категорию',
    description='Возвращает категорию по её ID.',
)
async def get_category(
    category_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> CategoryRead:
    """Получить категорию по ID."""
    return await get_category_or_404(category_id, session)


@router.post(
    '/',
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary='Создать категорию',
    description='Создаёт новую категорию. Имя должно быть уникальным.',
)
async def create_category(
    data: CategoryCreate,
    session: AsyncSession = Depends(get_async_session),
) -> CategoryRead:
    """Создать новую категорию с проверкой уникальности имени."""
    existing = await session.execute(select(Category).where(Category.name == data.name))
    if existing.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Category with this name already exists',
        )
    category = Category(**data.model_dump())
    session.add(category)
    await session.commit()
    await session.refresh(category)
    return category


@router.delete(
    '/{category_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary='Удалить категорию',
    description='Удаляет категорию по ID.',
)
async def delete_category(
    category_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Удалить категорию по ID."""
    category = await get_category_or_404(category_id, session)
    await session.delete(category)
    await session.commit()
