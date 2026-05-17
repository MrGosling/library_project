from backend.core.user import create_initial_users
from backend.core.initial_data import create_initial_data


async def init_db() -> None:
    await create_initial_users()
    await create_initial_data()
