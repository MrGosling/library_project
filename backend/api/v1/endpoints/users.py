from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.db import get_async_session
from backend.core.security import hash_password, verify_password
from backend.models.user import User
from backend.schemas.user import (
    UserCreate,
    UserLogin,
    UserRead,
    TokenResponse,
    ChangePassword,
    RefreshToken,
)

router = APIRouter()


@router.post(
    '/register', response_model=UserRead, status_code=status.HTTP_201_CREATED
)
async def register(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_async_session),
) -> User:
    """
    Регистрация нового пользователя.
    """
    existing_username = await session.execute(
        select(User).where(User.username == user_in.username)
    )
    if existing_username.scalar_one_or_none() is not None:
        raise HTTPException(
            status_code=400, detail='Username already registered'
        )

    existing_email = await session.execute(
        select(User).where(User.email == user_in.email)
    )
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
        is_superuser=False,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@router.post(
    '/login', response_model=TokenResponse, summary='Вход пользователя'
)
async def login(
    user_in: UserLogin,
    session: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    result = await session.execute(
        select(User).where(User.username == user_in.username)
    )
    user = result.scalar_one_or_none()
    if user is None or not verify_password(user_in.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
        )
    return TokenResponse(access_token=f'token_{user.id}')


@router.post(
    '/change-password', response_model=UserRead, summary='Смена пароля'
)
async def change_password(
    data: ChangePassword,
    session: AsyncSession = Depends(get_async_session),
) -> User:
    result = await session.execute(
        select(User).where(User.username == data.username)
    )
    user = result.scalar_one_or_none()
    if user is None or not verify_password(data.old_password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid username or password',
        )
    user.password = hash_password(data.new_password)
    await session.commit()
    await session.refresh(user)
    return user


@router.post(
    '/refresh-token', response_model=TokenResponse, summary='Обновление токена'
)
async def refresh_token(
    data: RefreshToken,
    session: AsyncSession = Depends(get_async_session),
) -> TokenResponse:
    if not data.token.startswith('token_'):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
        )
    user_id = data.token.replace('token_', '')
    user = await session.get(User, int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token',
        )
    return TokenResponse(access_token=f'token_{user.id}')
