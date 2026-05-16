from app.core.user import create_initial_users


async def init_db():
    await create_initial_users()
