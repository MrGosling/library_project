from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_session
from app.models.author import Author
from app.schemas.author import AuthorCreate, AuthorRead, AuthorUpdate

router = APIRouter(
    prefix="/authors",
    tags=["Authors"],
)


# Создать автора
@router.post(
    "",
    response_model=AuthorRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_author(
    author_data: AuthorCreate,
    session: AsyncSession = Depends(get_session),
):
    author = Author(**author_data.model_dump())

    session.add(author)
    await session.commit()
    await session.refresh(author)

    return author


# Получить авторов
@router.get(
    "",
    response_model=list[AuthorRead],
)
async def get_authors(
    search: str | None = Query(default=None, description="Поиск по ФИО автора"),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    statement = select(Author)

    if search:
        statement = statement.where(Author.full_name.ilike(f"%{search}%"))

    statement = (
        statement.order_by(Author.full_name).limit(limit=limit).offset(offset=offset)
    )

    result = await session.execute(statement)

    return result.scalars().all()


# Получить автора по айди
@router.get(
    "/{author_id}",
    response_model=AuthorRead,
)
async def get_author(
    author_id: int,
    session: AsyncSession = Depends(get_session),
):
    author = await session.get(Author, author_id)

    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автор не найден",
        )

    return author


# Обновить информацию у автора
@router.patch(
    "/{author_id}",
    response_model=AuthorRead,
)
async def update_author(
    author_id: int,
    author_data: AuthorUpdate,
    session: AsyncSession = Depends(get_session),
):
    author = await session.get(Author, author_id)

    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автор не найден",
        )

    update_data = author_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(author, field, value)

    await session.commit()
    await session.refresh(author)

    return author


# Удалить автора
@router.delete(
    "/{author_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_author(
    author_id: int,
    session: AsyncSession = Depends(get_session),
):
    author = await session.get(Author, author_id)

    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Автор не найден",
        )

    await session.delete(author)
    await session.commit()

    return None
