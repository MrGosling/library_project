from app.core.config import settings
import httpx


class GoogleBooksService:
    def __init__(self):
        self.base_url: str | None = settings.google_books_api_url
        self.api_key: str | None = settings.google_books_api_key

    async def search_books(self, query: str, lang: str = 'ru'):
        if not self.api_key:
            raise ValueError('Ключ Google Books API не задан')

        params: dict[str, str] = {'q': query, 'key': self.api_key}
        if lang:
            params['langRestrict'] = lang

        async with httpx.AsyncClient() as client:
            response: httpx.Response = await client.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()


google_books_service = GoogleBooksService()
