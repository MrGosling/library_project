from fastapi import FastAPI

from app.api.routes.authors import router as authors_router

# создает объект под приложение. Точка входа
app = FastAPI(title="Electronic Library API")


@app.get("/health")  # запрос на работоспособность сервера
async def health():
    return {"status": "ok"}


app.include_router(authors_router)
