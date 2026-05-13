import httpx
from fastapi import APIRouter, HTTPException

from app.schemas.ai import RecommendationRequest, RecommendationResponse
from app.services.ai_recommendations import AIRecommendationService

router = APIRouter(prefix='/ai', tags=['AI'])

ai_service = AIRecommendationService()


@router.post('/recommendations', response_model=RecommendationResponse)
async def get_book_recommendations(
    payload: RecommendationRequest,
) -> RecommendationResponse:
    try:
        return await ai_service.recommend_books(payload)

    except httpx.ConnectError as exc:
        raise HTTPException(
            status_code=503,
            detail='Ollama сервис не доступен. Проверьте, что ollama контейнер запущен.',
        ) from exc

    except ValueError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc


@router.get('/health')
async def ai_health() -> dict:
    try:
        return await ai_service.ollama.health()

    except httpx.HTTPError as exc:
        raise HTTPException(
            status_code=503,
            detail='Ollama сервис недоступен.',
        ) from exc
