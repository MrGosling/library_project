from app.core.db import Base, engine
from app.core.user import create_initial_users


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await create_initial_users()
