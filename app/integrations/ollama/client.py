import httpx

from app.core.config import settings


class OllamaClient:
    def __init__(self) -> None:
        self.base_url = settings.ollama_base_url
        self.model = settings.ollama_model
        self.timeout = settings.ollama_timeout

    async def generate(self, prompt: str, *, json_mode: bool = True) -> str:
        payload = {
            'model': self.model,
            'prompt': prompt,
            'stream': False,
            'options': {
                'temperature': 0.3,
            },
        }

        if json_mode:
            payload['format'] = 'json'

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        ) as client:
            response = await client.post('/api/generate', json=payload)
            response.raise_for_status()
            data = response.json()

        return data.get('response', '')

    async def health(self) -> dict:
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=5.0,
        ) as client:
            response = await client.get('/api/tags')
            response.raise_for_status()
            return response.json()
