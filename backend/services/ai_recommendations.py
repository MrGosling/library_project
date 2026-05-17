import json

from backend.core.config import settings
from backend.integrations.ollama.client import OllamaClient
from backend.schemas.ai import (
    RecommendationItem,
    RecommendationRequest,
    RecommendationResponse,
)


class AIRecommendationService:
    def __init__(self) -> None:
        self.ollama = OllamaClient()

    async def recommend_books(
        self,
        payload: RecommendationRequest,
    ) -> RecommendationResponse:
        prompt = self._build_prompt(payload)
        raw_response = await self.ollama.generate(prompt, json_mode=True)

        recommendations = self._parse_recommendations(raw_response)

        return RecommendationResponse(
            provider='ollama',
            model=settings.ollama_model,
            recommendations=recommendations,
        )

    def _build_prompt(self, payload: RecommendationRequest) -> str:
        read_books_text = '\n'.join(
            [
                f'{i + 1}. id={book.id}; title={book.title}; '
                f'author={book.author}; genre={book.genre}; description={book.description}'
                for i, book in enumerate(payload.read_books)
            ]
        )

        catalog_text = '\n'.join(
            [
                f'{i + 1}. id={book.id}; title={book.title}; '
                f'author={book.author}; genre={book.genre}; description={book.description}'
                for i, book in enumerate(payload.catalog)
            ]
        )

        return f"""
Ты — AI-модуль электронной библиотеки.

Твоя задача: порекомендовать пользователю книги на основе его истории чтения.

История чтения пользователя:
{read_books_text}

Доступный каталог библиотеки:
{catalog_text}

Правила:
1. Рекомендуй только книги из доступного каталога.
2. Не рекомендуй книги, которые пользователь уже прочитал.
3. Не выдумывай книги, авторов и id.
4. Верни максимум {payload.limit} рекомендаций.
5. Для каждой рекомендации укажи короткую причину на русском языке.
6. Ответ верни строго в JSON без markdown.

Формат ответа:
{{
  "recommendations": [
    {{
      "id": "id книги из каталога",
      "title": "название книги",
      "author": "автор",
      "reason": "почему эта книга подходит пользователю"
    }}
  ]
}}
"""

    def _parse_recommendations(
        self, raw_response: str
    ) -> list[RecommendationItem]:
        try:
            parsed = json.loads(raw_response)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f'Model returned invalid JSON: {raw_response}'
            ) from exc

        if isinstance(parsed, list):
            items = parsed
        else:
            items = parsed.get('recommendations', [])

        return [RecommendationItem.model_validate(item) for item in items]
