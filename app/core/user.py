import contextlib
from typing import AsyncGenerator

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.models.user import User


@contextlib.asynccontextmanager
async def get_async_session_context() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


async def create_user(email: str, password: str, is_superuser: bool = False) -> None:
    async with get_async_session_context() as session:
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if user is None:
            new_user = User(email=email, password=password, is_superuser=is_superuser)
            session.add(new_user)
            await session.commit()


async def create_first_superuser() -> None:
    email = settings.first_superuser_email
    password = settings.first_superuser_password
    if email and password:
        await create_user(
            email=email,
            password=password,
            is_superuser=True,
        )


async def create_initial_users() -> None:
    await create_first_superuser()

    await create_user(email='user@example.com', password='user_password')
