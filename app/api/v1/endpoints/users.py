from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

router = APIRouter()


@router.post('/register', response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Регистрация нового пользователя.
    """
    existing_username = await session.execute(select(User).where(User.username == user_in.username))
    if existing_username.scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail='Username already registered')

    existing_email = await session.execute(select(User).where(User.email == user_in.email))
    if existing_email.scalar_one_or_none() is not None:
        raise HTTPException(status_code=400, detail='Email already registered')

    user = User(
        username=user_in.username,
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        password=hash_password(user_in.password),
        role='reader',
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
