from fastapi import APIRouter

router = APIRouter(prefix='/health', tags=['Health'])


@router.get('/', summary='Проверка состояния сервиса')
async def health_check() -> dict:
    """Возвращает статус сервиса."""
    return {'status': 'ok'}
