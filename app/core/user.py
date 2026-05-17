import contextlib
from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models.user import User, UserRole


@contextlib.asynccontextmanager
async def get_async_session_context() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def create_user(
    username: str,
    email: str,
    password: str,
    role: UserRole = UserRole.READER,
    is_superuser: bool = False,
) -> None:
    async with get_async_session_context() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if user is None:
            new_user = User(
                username=username,
                email=email,
                password=password,
                role=role,
                is_superuser=is_superuser,
            )
            session.add(new_user)
            await session.commit()


async def create_first_superuser() -> None:
    email = settings.first_superuser_email
    password = settings.first_superuser_password
    if email and password:
        await create_user(
            username=UserRole.ADMIN,
            email=email,
            password=password,
            role=UserRole.ADMIN,
            is_superuser=True,
        )


async def create_initial_users() -> None:
    print('Creating initial superuser...')
    await create_first_superuser()
    print('Creating initial user...')
    await create_user(
        username='user',
        email='user@example.com',
        password='user_password',
        role=UserRole.READER,
    )
